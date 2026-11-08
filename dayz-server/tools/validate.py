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


def parse_xml(path: Path) -> ET.Element | None:
    """Parse once per file so a broken file is only reported once."""
    if path not in _xml_cache:
        try:
            _xml_cache[path] = ET.parse(path).getroot()
        except ET.ParseError as e:
            err(path, f"XML is not well-formed: {e}")
            _xml_cache[path] = None
    return _xml_cache[path]


def check_json(path: Path) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        err(path, f"invalid JSON at line {e.lineno} col {e.colno}: {e.msg}")


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
            err(path, f"line {n}: missing ';' -> {line}")
        m = re.match(r'(\w+)\s*=\s*"(.*)"\s*;', line)
        if m and m.group(1) in SECRET_KEYS:
            key, value = m.groups()
            if value not in SECRET_KEYS[key]:
                err(path, f"line {n}: {key} holds a real value. Keep "
                          f'it blank in the repo; set it on the server.')

    m = re.search(r'template\s*=\s*"([^"]+)"', text)
    if not m:
        err(path, "no mission template set in class Missions")
    else:
        mission = path.parent / "mpmissions" / m.group(1)
        if (path.parent / "mpmissions").is_dir() and not mission.is_dir():
            err(path, f"template '{m.group(1)}' has no folder at {mission}")


def check_types(path: Path, root: ET.Element, seen: dict[str, Path]) -> None:
    for t in root.iter("type"):
        name = t.get("name")
        if not name:
            err(path, "<type> without a name attribute")
            continue
        if name in seen:
            where = "this file" if seen[name] == path else str(seen[name])
            warn(path, f"'{name}' is already defined in {where}")
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
                err(path, f"'{name}' <{field}> is not a whole number: {el.text!r}")
        # nominal 0 means "never spawns"; vanilla leaves min > 0 on those
        if ("min" in vals and vals.get("nominal", 0) > 0
                and vals["min"] > vals["nominal"]):
            err(path, f"'{name}' min ({vals['min']}) > nominal ({vals['nominal']})")
        if ("quantmin" in vals and "quantmax" in vals
                and vals["quantmin"] > vals["quantmax"]):
            err(path, f"'{name}' quantmin > quantmax")


def check_mission(mission: Path) -> None:
    seen_types: dict[str, Path] = {}

    vanilla_types = mission / "db" / "types.xml"
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
        folder = mission / ce.get("folder", "")
        for f in ce.iter("file"):
            target = folder / f.get("name", "")
            if not target.is_file():
                err(core, f"lists {target.relative_to(mission)} but it doesn't exist")
                continue
            if f.get("type") == "types":
                troot = parse_xml(target)
                if troot is not None:
                    check_types(target, troot, seen_types)


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not base.is_dir():
        print(f"Not a folder: {base}")
        return 2

    skip = {".git", "storage_1", "storage_2", "storage_3", "storage_4"}
    files = [p for p in base.rglob("*")
             if p.is_file() and not skip.intersection(p.parts)]

    for p in files:
        suffix = p.suffix.lower()
        if suffix == ".xml":
            parse_xml(p)
        elif suffix == ".json":
            check_json(p)
        elif p.name.lower() == "serverdz.cfg":
            check_server_cfg(p)

    missions = base / "mpmissions"
    if missions.is_dir():
        for mission in sorted(m for m in missions.iterdir() if m.is_dir()):
            check_mission(mission)

    for line in warnings + errors:
        print(line)
    xml_json = sum(p.suffix.lower() in (".xml", ".json") for p in files)
    print(f"\nChecked {xml_json} XML/JSON files under {base}: "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
