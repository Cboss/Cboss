#!/usr/bin/env python3
"""Merge a map author's DayZ XML file with Bohemia's vanilla one, entry by entry.

Used by build_masters.py for files made of named entries:
mapclusterproto.xml (<export>, <cluster>) and events.xml (<event>).

The map author's file is the starting point and every line of it is kept, in
order, except entries the recipe drops or replaces. Vanilla entries are
copied in character for character, between marker comments. Entries in both
files that differ are conflicts: the map's version stays until Boss decides.

Run directly to compare two versions of a file at the entry level:
    python3 tools/merge_entries.py OLD.xml NEW.xml
"""
from __future__ import annotations

import hashlib
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

MARK = "build_masters.py"

# Entry tags per root element: (tag, self-closing?)
KINDS = {"prototype": [("export", True), ("cluster", False)],
         "events": [("event", False)],
         "spawnabletypes": [("type", False)]}


@dataclass
class Entry:
    kind: str
    name: str
    first: int          # first line index (0-based, inclusive)
    last: int           # last line index (inclusive)
    canon: tuple        # normalised content, for comparing

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.name}"


@dataclass
class EntryFile:
    path: Path
    raw: bytes
    bom: bool
    newline: str
    lines: list[str]
    root: str = ""
    entries: dict[str, Entry] = field(default_factory=dict)
    last_end: dict[str, int] = field(default_factory=dict)  # kind -> last line
    duplicates: list[str] = field(default_factory=list)

    @property
    def line_count(self) -> int:
        return len(self.lines) - (self.lines[-1] == "")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    def block(self, e: Entry) -> list[str]:
        return self.lines[e.first:e.last + 1]

    def keys(self, kind: str) -> list[str]:
        return [k for k, e in self.entries.items() if e.kind == kind]


def canon(el: ET.Element) -> tuple:
    return (el.tag,
            tuple(sorted((k, v.strip()) for k, v in el.attrib.items())),
            (el.text or "").strip(),
            tuple(canon(c) for c in el))


def mask_comments(text: str) -> str:
    """Blank out <!-- --> comments, keeping offsets and line breaks."""
    return re.sub(r"<!--.*?-->",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  text, flags=re.S)


def decode(raw: bytes) -> tuple[bool, str, str]:
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw[3 if bom else 0:].decode("utf-8")
    crlf = text.count("\r\n")
    newline = "\r\n" if crlf and crlf >= text.count("\n") - crlf else "\n"
    return bom, text, newline


def load(path: Path, raw: bytes | None = None) -> EntryFile:
    raw = path.read_bytes() if raw is None else raw
    bom, text, newline = decode(raw)
    ef = EntryFile(path, raw, bom, newline, text.split(newline))
    try:
        ef.root = ET.fromstring(raw).tag
    except ET.ParseError as e:
        raise SystemExit(f"{path}: XML is not well-formed: {e}")
    if ef.root not in KINDS:
        raise SystemExit(f"{path}: don't know the entries of <{ef.root}> files")

    masked = mask_comments(text)
    starts = [0]
    for ln in ef.lines[:-1]:
        starts.append(starts[-1] + len(ln) + len(newline))

    def line_of(off: int) -> int:
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo

    for tag, selfclosing in KINDS[ef.root]:
        pattern = (rf"<{tag}\b[^>]*?/>" if selfclosing
                   else rf"<{tag}\b[^>]*?(?:/>|>.*?</{tag}>)")
        for m in re.finditer(pattern, masked, flags=re.S):
            n = re.search(r'\bname="([^"]*)"', m.group(0))
            if not n:
                continue
            e = Entry(tag, n.group(1), line_of(m.start()), line_of(m.end() - 1),
                      canon(ET.fromstring(m.group(0))))
            if e.key in ef.entries:
                ef.duplicates.append(e.key)
            else:
                ef.entries[e.key] = e
            ef.last_end[tag] = max(ef.last_end.get(tag, -1), e.last)
    return ef


def indent_of(line: str) -> str:
    return line[:len(line) - len(line.lstrip())]


def lst(keys) -> str:
    keys = list(keys)
    return ", ".join(f"`{k}`" for k in keys) if keys else "none"


@dataclass
class Result:
    output: bytes
    report: list[str]
    problems: list[str]
    undecided: list[str]


def merge(step: dict, here: Path, map_label: str, van_label: str) -> Result:
    map_label = step.get("map_label", map_label)
    van_label = step.get("vanilla_label", van_label)
    """step keys: map, vanilla, output, add_vanilla ("all" or list),
    skip_vanilla (list), drop_map ({key: why}), decisions ({key: {keep, why}}),
    replace_map ({key: {name, children: [[type, min, max], ...], why}}: keep the
    map entry's settings but rename it and swap its <child> list; events only),
    prefer ({"keep": "map"|"vanilla", "why": ...}: default for conflicts with
    no decision; without it they are reported as waiting on Boss)."""
    mp = load(here / step["map"])
    va = load(here / step["vanilla"])
    decisions: dict = step.get("decisions", {})
    drop: dict = step.get("drop_map", {})
    swap: dict = step.get("replace_map", {})
    skip = set(step.get("skip_vanilla", []))
    add_spec = step.get("add_vanilla", "all")
    problems: list[str] = []
    if mp.root != va.root:
        raise SystemExit(f"{step['map']} and {step['vanilla']} are different file types")
    for ef in (mp, va):
        if ef.duplicates:
            problems.append(f"{ef.path.name}: defined twice: {ef.duplicates}")
    for k, d in decisions.items():
        if d.get("keep") not in ("map", "vanilla"):
            raise SystemExit(f"{k}: keep must be 'map' or 'vanilla'")

    only_van = [k for k in va.entries if k not in mp.entries]
    only_map = [k for k in mp.entries if k not in va.entries]
    wanted = only_van if add_spec == "all" else [k for k in only_van if k in add_spec]
    added = [k for k in wanted if k not in skip]
    not_added = [k for k in only_van if k not in added]
    dropped = [k for k in drop if k in mp.entries]
    swapped = [k for k in swap if k in mp.entries]
    if set(swapped) & set(dropped):
        raise SystemExit(f"both dropped and replaced: {sorted(set(swapped) & set(dropped))}")
    new_key = {k: f"{k.split(':')[0]}:{swap[k].get('name') or k.split(':', 1)[1]}" for k in swapped}
    conflicts = [k for k in mp.entries if k in va.entries and k not in drop and k not in swap
                 and mp.entries[k].canon != va.entries[k].canon]
    prefer = step.get("prefer")
    if prefer and prefer.get("keep") not in ("map", "vanilla"):
        raise SystemExit("prefer.keep must be 'map' or 'vanilla'")
    undecided = [] if prefer else [k for k in conflicts if k not in decisions]
    choice = {k: decisions.get(k, prefer or {"keep": "map"}) for k in conflicts}
    use_vanilla = [k for k in conflicts if choice[k]["keep"] == "vanilla"]
    stale = [k for k in decisions if k not in conflicts]
    stale = stale + [k for k in drop if k not in mp.entries]
    stale = stale + [k for k in swap if k not in mp.entries]
    if add_spec != "all":
        stale += [k for k in add_spec if k not in only_van]
    stale += [k for k in skip if k not in only_van]

    # Line plan, keyed on map line numbers so map lines never reorder.
    replace = {mp.entries[k].first: k for k in use_vanilla}
    removed = {mp.entries[k].first: k for k in dropped}
    skip_lines: set[int] = set()
    swap_at = {mp.entries[k].first: k for k in swapped}
    for k in use_vanilla + dropped + swapped:
        e = mp.entries[k]
        skip_lines.update(range(e.first + 1, e.last + 1))

    def swapped_block(k: str) -> list[str]:
        old = mp.block(mp.entries[k])
        spec = swap[k]
        first = old[0]
        if spec.get("name"):
            first = re.sub(r'name="[^"]*"', f'name="{spec["name"]}"', first, count=1)
        try:
            a = next(i for i, l in enumerate(old) if "<children" in l)
            b = next(i for i, l in enumerate(old) if "</children>" in l)
        except StopIteration:
            raise SystemExit(f"{k}: replace_map needs a <children> list")
        cind = indent_of(old[a]) + (indent_of(old[a])[-1:] or "\t")
        kids = [f'{cind}<child lootmax="0" lootmin="0" max="{mx}" min="{mn}" type="{t}"/>'
                for t, mn, mx in spec["children"]]
        return [first] + old[1:a + 1] + kids + old[b:]

    inserts: dict[int, list[str]] = {}
    for tag, _ in KINDS[mp.root]:
        keys = [k for k in added if k.startswith(tag + ":")]
        if not keys:
            continue
        at = mp.last_end.get(tag)
        if at is None:
            raise SystemExit(f"{step['map']}: no <{tag}> to add vanilla entries after")
        ind = indent_of(mp.lines[mp.entries[mp.keys(tag)[0]].first]) or "\t"
        block = [f"{ind}<!-- {MARK}: added from {van_label} -->"]
        for k in keys:
            block += va.block(va.entries[k])
        block.append(f"{ind}<!-- {MARK}: end of added block -->")
        inserts[at] = block

    out: list[str] = []
    for i, line in enumerate(mp.lines):
        if i in replace:
            k = replace[i]
            out.append(f"{indent_of(line)}<!-- {MARK}: vanilla version of {k} "
                       f"(decision in the recipe) -->")
            out += va.block(va.entries[k])
        elif i in swap_at:
            k = swap_at[i]
            out.append(f"{indent_of(line)}<!-- {MARK}: replaced {k}: {swap[k].get('why', '')} -->")
            out += swapped_block(k)
        elif i in removed:
            k = removed[i]
            out.append(f"{indent_of(line)}<!-- {MARK}: removed {k}: {drop[k]} -->")
        elif i not in skip_lines:
            out.append(line)
        if i in inserts:
            out += inserts[i]
    data = (b"\xef\xbb\xbf" if mp.bom else b"") + mp.newline.join(out).encode("utf-8")

    # Verify before anything is written.
    try:
        ms = load(Path(step["output"]), data)
    except SystemExit as e:
        problems.append(f"master: {e}")
    else:
        want = (set(mp.entries) - set(dropped) - set(swapped)) | set(added) | set(new_key.values())
        if set(ms.entries) != want:
            problems.append(f"master entries differ from expected: missing "
                            f"{sorted(want - set(ms.entries))}, extra "
                            f"{sorted(set(ms.entries) - want)}")
        if ms.duplicates:
            problems.append(f"master defines twice: {ms.duplicates}")
        for k, e in ms.entries.items():
            if k in new_key.values():
                continue
            src = va if (k in added or k in use_vanilla) else mp
            if k in src.entries and e.canon != src.entries[k].canon:
                problems.append(f"master {k} does not match its source")
        if ms.newline != mp.newline or ms.bom != mp.bom:
            problems.append("master line endings/BOM differ from the map file")
    kept = [l for i, l in enumerate(mp.lines)
            if i not in skip_lines and i not in replace and i not in removed and i not in swap_at]
    it = iter(out)
    if not all(any(l == o for o in it) for l in kept):
        problems.append("some of the map's own lines are missing from the master")

    # Report section.
    name = Path(step["output"]).name
    r = [f"## {name}", "",
         f"Entry merge: `{step['map']}` ({map_label}) + `{step['vanilla']}` "
         f"({van_label}) → `{step['output']}`.", "",
         "| | sha256 | Lines | Entries |", "|---|---|---|---|"]
    for label, ef in ((map_label, mp), (van_label, va)):
        r.append(f"| {label} | `{ef.sha256[:12]}` | {ef.line_count} | {len(ef.entries)} |")
    r += [f"| **Master** | `{hashlib.sha256(data).hexdigest()[:12]}` | "
          f"{len(out) - (out[-1] == '')} | {len(set(mp.entries) - set(dropped)) + len(added)} |", "",
          f"Verification: {'**FAILED**' if problems else 'passed'}. "
          f"Line endings: {'CRLF' if mp.newline == chr(13) + chr(10) else 'LF'}, as in the map file.", ""]
    if problems:
        r += ["**Problems:**", ""] + [f"- {p}" for p in problems] + [""]
    r += ["**Conflicts** (same name, different content):", ""]
    if conflicts:
        r += ["| Entry | Kept | Why |", "|---|---|---|"]
        for k in conflicts:
            if k in decisions:
                kept, why = decisions[k]["keep"], decisions[k].get("why", "")
            elif prefer:
                kept, why = f"{prefer['keep']} (file default)", prefer.get("why", "")
            else:
                kept, why = "map (**undecided**, waiting on Boss)", ""
            r.append(f"| `{k}` | {kept} | {why} |")
        r.append("")
        for k in conflicts:
            r += [f"<details><summary><code>{k}</code></summary>", "", "```xml",
                  f"<!-- {map_label} -->"] + mp.block(mp.entries[k]) + \
                 [f"<!-- {van_label} -->"] + va.block(va.entries[k]) + \
                 ["```", "", "</details>", ""]
    else:
        r += ["none", ""]
    if swapped:
        r += ["**Replaced in the map file** (settings kept, children swapped):", "",
              "| Was | Now | Children | Why |", "|---|---|---|---|"]
        for k in swapped:
            kids = ", ".join(f"`{t}` {mn}-{mx}" for t, mn, mx in swap[k]["children"])
            r.append(f"| `{k}` | `{new_key[k]}` | {kids} | {swap[k].get('why', '')} |")
        r.append("")
    r += [f"**Removed from the map file:** {lst(f'{k} ({drop[k]})' for k in dropped)}", "",
          f"**Added from {van_label}:** {lst(added)}", "",
          f"**Only in {van_label}, not added:** {lst(not_added)}", "",
          f"**Only in the map file, kept:** {len(only_map) - len(dropped)}", ""]
    if mp.root == "prototype":
        ex = {e.name for e in mp.entries.values() if e.kind == "export"}
        cl = {e.name for e in mp.entries.values() if e.kind == "cluster"}
        r += [f"Map clusters with no export (no model to attach to): {lst(sorted(cl - ex))}. "
              f"Map exports with no cluster: {lst(sorted(ex - cl))}.", ""]
    if stale:
        r += [f"Recipe entries that no longer apply (safe to remove): {lst(stale)}", ""]
    return Result(data, r, problems, undecided)


def diff(old: Path, new: Path, old_raw: bytes | None = None) -> int:
    a, b = load(old, old_raw), load(new)
    print(f"old: {old}  sha256 {a.sha256[:12]}  {a.line_count} lines")
    print(f"new: {new}  sha256 {b.sha256[:12]}  {b.line_count} lines")
    if a.raw == b.raw:
        print("identical")
        return 0
    if a.newline != b.newline:
        print(f"line endings changed: {a.newline!r} -> {b.newline!r}")
    for tag, _ in KINDS[b.root]:
        ka, kb = set(a.keys(tag)), set(b.keys(tag))
        changed = sorted(k for k in ka & kb if a.entries[k].canon != b.entries[k].canon)
        print(f"== {tag}: {len(ka)} -> {len(kb)}")
        print(f"  removed: {sorted(ka - kb)}")
        print(f"  added:   {sorted(kb - ka)}")
        print(f"  changed: {changed}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(diff(Path(sys.argv[1]), Path(sys.argv[2])))
