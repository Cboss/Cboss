#!/usr/bin/env python3
"""Check DayZ server config files before they go on the server.

Catches the mistakes that stop a DayZ server from booting or silently
break the loot economy:

  * XML that isn't well-formed (one missing '>' kills the whole file)
  * JSON that isn't strict JSON (DayZ rejects comments and trailing commas)
  * serverDZ.cfg lines missing their ';' or holding a real password
  * types entries with min > nominal, quantmin > quantmax, or missing fields
  * the same type defined twice across db/types.xml and the custom files
  * custom files listed in cfgeconomycore.xml that don't exist

Usage:
    python3 tools/validate.py                 # check this repo's dayz-server/
    python3 tools/validate.py D:/DayZServer   # check a live server folder

Standard library only, so it runs anywhere Python 3.8+ does, Windows included.
Exits 1 if any ERROR is found; WARNs alone exit 0.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PLACEHOLDER = "CHANGE_ME"
# Password fields that must never hold a real value in a public repo.
# Blank ("") is allowed: the live configs keep them blank in the file.
SECRET_KEYS = {"passwordAdmin": {PLACEHOLDER, ""}, "password": {PLACEHOLDER, ""}}
REQUIRED_TYPE_FIELDS = ("nominal", "lifetime", "restock", "min",
                        "quantmin", "quantmax", "cost")

errors: list[str] = []
warnings: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"ERROR {path}: {msg}")


def warn(path: Path, msg: str) -> None:
    warnings.append(f"WARN  {path}: {msg}")


_xml_cache: dict[Path, ET.Element | None] = {}


def is_original(path: Path) -> bool:
    """Files under originals/ are kept exactly as received, so problems in
    them are reported as warnings: they are the author's to fix, and the
    merge or our own copy is where they get handled."""
    return "originals" in path.parts


def problem(path: Path, msg: str) -> None:
    if is_original(path):
        warn(path, f"(original, kept as received) {msg}")
    else:
        err(path, msg)


def parse_xml(path: Path) -> ET.Element | None:
    """Parse once per file so a broken file is only reported once."""
    if path not in _xml_cache:
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as e:
            problem(path, f"XML is not well-formed: {e}")
            root = None
        else:
            # Text after a tag (e.g. '<pos .../>sa') is legal XML but is
            # never meaningful in DayZ files: it is almost always a typo.
            for el in root.iter():
                if el.tail and el.tail.strip():
                    warn(path, f"stray text {el.tail.strip()[:30]!r} after "
                               f"<{el.tag} {' '.join(f'{k}={v!r}' for k, v in list(el.attrib.items())[:3])}>")
        _xml_cache[path] = root
    return _xml_cache[path]


def check_json(path: Path) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        problem(path, f"invalid JSON at line {e.lineno} col {e.colno}: {e.msg}")


def strip_cfg_comment(line: str) -> str:
    """Remove a // comment that isn't inside a quoted string."""
    in_str = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_str = not in_str
        elif not in_str and line.startswith("//", i):
            return line[:i]
    return line


def check_server_cfg(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig")
    in_block_comment = False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
            continue
        if line.startswith("/*"):
            in_block_comment = "*/" not in line
            continue
        line = strip_cfg_comment(line).strip()
        if not line or line in ("{", "}", "};") or line.startswith("class "):
            continue
        if "=" in line and not line.endswith(";"):
            problem(path, f"line {n}: missing ';' -> {line}")
        m = re.match(r'(\w+)\s*=\s*"(.*)"\s*;', line)
        if m and m.group(1) in SECRET_KEYS:
            key, value = m.groups()
            if value not in SECRET_KEYS[key]:
                problem(path, f"line {n}: {key} holds a real value. Keep "
                          f'it blank in the repo; set it on the server.')

    m = re.search(r'template\s*=\s*"([^"]+)"', text)
    if not m:
        problem(path, "no mission template set in class Missions")
    else:
        mission = path.parent / "mpmissions" / m.group(1)
        if (path.parent / "mpmissions").is_dir() and not mission.is_dir():
            problem(path, f"template '{m.group(1)}' has no folder at {mission}")


def check_types(path: Path, root: ET.Element, seen: dict[str, Path]) -> None:
    for t in root.iter("type"):
        name = t.get("name")
        if not name:
            problem(path, "<type> without a name attribute")
            continue
        if name in seen:
            where = "this file" if seen[name] == path else str(seen[name])
            warn(path, f"'{name}' is already defined in {where}")
        else:
            twin = next((n for n in seen if n.lower() == name.lower()), None)
            if twin:
                where = "this file" if seen[twin] == path else str(seen[twin])
                warn(path, f"'{name}' differs only in letter case from "
                           f"'{twin}' in {where}; DayZ class names ignore case, "
                           f"so this is likely a duplicate")
        seen[name] = path

        vals: dict[str, int] = {}
        for field in REQUIRED_TYPE_FIELDS:
            el = t.find(field)
            if el is None or el.text is None:
                # nominal 0 items (e.g. crafted-only) often omit fields
                if t.findtext("nominal", "0").strip() != "0":
                    warn(path, f"'{name}' has no <{field}>")
                continue
            try:
                vals[field] = int(el.text.strip())
            except ValueError:
                problem(path, f"'{name}' <{field}> is not a whole number: {el.text!r}")
        # nominal 0 means "never spawns"; vanilla leaves min > 0 on those
        if ("min" in vals and vals.get("nominal", 0) > 0
                and vals["min"] > vals["nominal"]):
            problem(path, f"'{name}' min ({vals['min']}) > nominal ({vals['nominal']})")
        if ("quantmin" in vals and "quantmax" in vals
                and vals["quantmin"] > vals["quantmax"]):
            problem(path, f"'{name}' quantmin > quantmax")


def check_environment(path: Path) -> None:
    """Cross-check cfgenvironment.xml against the env/ files next to it."""
    root = parse_xml(path)
    if root is None:
        return
    base = path.parent
    loaded: dict[str, str] = {}
    for f in root.iter("file"):
        rel = f.get("path")
        if not rel:
            continue
        stem = Path(rel).stem
        loaded[stem] = rel
        target = find(base, rel)
        if target.is_file():
            continue
        folder = target.parent
        twin = [p.name for p in folder.glob("*") if p.name.lower() == target.name.lower()] \
            if folder.is_dir() else []
        if twin:
            problem(path, f"loads {rel} but the file is named {twin[0]} "
                          f"(case matters on Linux servers)")
        else:
            problem(path, f"loads {rel} but it doesn't exist")
    used = {f.get("usable") for f in root.iter("file") if f.get("usable")}
    for u in sorted(used - set(loaded)):
        problem(path, f"a territory uses '{u}' but no <file path> loads it")
    env = find(base, "env")
    if env.is_dir():
        loaded_lower = {Path(r).name.lower() for r in loaded.values()}
        for p in sorted(env.glob("*.xml")):
            if p.name.lower() not in loaded_lower:
                warn(path, f"env/{p.name} is not loaded by cfgenvironment.xml")
    for stem in sorted(set(loaded) - used):
        warn(path, f"loads {loaded[stem]} but no territory uses it")


_overlay: dict[Path, Path] = {}


def find(folder: Path, rel: str) -> Path:
    """Resolve a mission file. A built master folder (e.g. sahrani-plus/
    mission/) holds only the files we change; the rest come from the
    originals named by "base" in the masters.json next to it."""
    folder = folder.resolve()
    p = folder / rel
    if p.exists():
        return p
    for top, base in _overlay.items():
        try:
            sub = folder.relative_to(top)
        except ValueError:
            continue
        q = base / sub / rel
        if q.exists():
            return q
    return p


def register_overlays(files: list[Path]) -> None:
    for recipe in (p for p in files if p.name == "masters.json"):
        try:
            rec = json.loads(recipe.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if "base" in rec:
            _overlay[(recipe.parent / rec.get("mission", "mission")).resolve()] = \
                (recipe.parent / rec["base"]).resolve()


LIMIT_KINDS = {"category": "categories", "usage": "usageflags",
               "value": "valueflags", "tag": "tags"}


def load_limits(mission: Path) -> dict[str, set[str]] | None:
    """Names defined in cfglimitsdefinition.xml (+ user groups)."""
    path = find(mission, "cfglimitsdefinition.xml")
    if not path.is_file():
        return None
    root = parse_xml(path)
    if root is None:
        return None
    limits = {k: set() for k in LIMIT_KINDS}
    for kind, section in LIMIT_KINDS.items():
        for sec in root.iter(section):
            limits[kind].update(e.get("name", "") for e in sec.iter(kind))
    user = find(mission, "cfglimitsdefinitionuser.xml")
    if user.is_file():
        uroot = parse_xml(user)
        if uroot is not None:
            for kind in ("usage", "value"):
                for sec in uroot.iter(LIMIT_KINDS[kind]):
                    limits[kind].update(u.get("name", "") for u in sec.iter("user"))
    return limits


def check_limits(path: Path, root: ET.Element, limits: dict[str, set[str]]) -> None:
    missing: dict[tuple[str, str], list[str]] = {}
    for t in root.iter("type"):
        for kind in LIMIT_KINDS:
            for el in t.iter(kind):
                n = el.get("name") or el.get("user")
                if n and n not in limits[kind]:
                    missing.setdefault((kind, n), []).append(t.get("name", "?"))
    for (kind, n), items in sorted(missing.items()):
        shown = ", ".join(items[:5]) + (f" and {len(items) - 5} more" if len(items) > 5 else "")
        problem(path, f"{kind} '{n}' is not defined in cfglimitsdefinition.xml "
                      f"(used by {shown})")


def check_mission(mission: Path) -> None:
    seen_types: dict[str, Path] = {}
    limits = load_limits(mission)

    vanilla_types = find(mission, "db/types.xml")
    if vanilla_types.is_file():
        root = parse_xml(vanilla_types)
        if root is not None:
            check_types(vanilla_types, root, seen_types)

    core = mission / "cfgeconomycore.xml"
    if not core.is_file():
        return
    root = parse_xml(core)
    if root is None:
        return
    for ce in root.iter("ce"):
        for f in ce.iter("file"):
            target = find(mission, f"{ce.get('folder', '')}/{f.get('name', '')}")
            if not target.is_file():
                msg = f"lists {ce.get('folder', '')}/{f.get('name', '')} but it doesn't exist"
                if mission.resolve() in _overlay:
                    # A built master: the file may only be on the server so far.
                    warn(core, msg + " in the repo yet (send it, or confirm it's on the server)")
                else:
                    problem(core, msg)
                continue
            if f.get("type") == "types":
                troot = parse_xml(target)
                if troot is not None:
                    check_types(target, troot, seen_types)
                    if limits is not None:
                        check_limits(target, troot, limits)


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not base.is_dir():
        print(f"Not a folder: {base}")
        return 2

    skip = {".git", "storage_1", "storage_2", "storage_3", "storage_4"}
    files = [p for p in base.rglob("*")
             if p.is_file() and not skip.intersection(p.parts)]
    register_overlays(files)

    for p in files:
        suffix = p.suffix.lower()
        if suffix == ".xml":
            parse_xml(p)
        elif suffix == ".json":
            check_json(p)
        elif p.name.lower() == "serverdz.cfg":
            check_server_cfg(p)
    for p in files:
        if p.name.lower() == "cfgenvironment.xml":
            check_environment(p)

    # A mission is any folder with a cfgeconomycore.xml (mpmissions/<name>/,
    # originals/<map>/, or the folder passed on the command line).
    for mission in sorted({p.parent for p in files
                           if p.name.lower() == "cfgeconomycore.xml"}):
        check_mission(mission)

    for line in warnings + errors:
        print(line)
    xml_json = sum(p.suffix.lower() in (".xml", ".json") for p in files)
    print(f"\nChecked {xml_json} XML/JSON files under {base}: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
