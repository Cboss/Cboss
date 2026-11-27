#!/usr/bin/env python3
"""Merge a map's mapclusterproto.xml with Bohemia's vanilla one, repeatably.

The map author's file is the starting point and is kept line for line.
Entries that only exist in the vanilla file are copied in verbatim, under a
comment saying where they came from. Entries that exist in both but differ
are conflicts: the map's version is kept until Boss decides otherwise in
merge.json.

Commands:
    build  MERGE_JSON   write the master and MERGE_REPORT.md
    check  MERGE_JSON   rebuild in memory; fail if the committed master or
                        report is out of date (used by CI)
    diff   OLD NEW      entry-level comparison of two mapclusterproto.xml
                        files, e.g. an old and a new version of an original

Options for build/check:
    --strict            also fail if any conflict has no decision yet

merge.json (paths are relative to the merge.json file):
    {
      "map":        "../originals/<map>/mapclusterproto.xml",
      "map_label":  "Sahrani Plus (map author)",
      "vanilla":    "../originals/vanilla-chernarusplus/mapclusterproto.xml",
      "vanilla_label": "Bohemia vanilla Chernarus",
      "output":     "mission/mapclusterproto.xml",
      "report":     "MERGE_REPORT.md",
      "decisions":  {"export:AppleTree2": {"keep": "map", "why": "..."}},
      "skip_vanilla": ["cluster:Rail9"]
    }

    "keep" is "map" or "vanilla". Keys are "export:<name>" or
    "cluster:<name>". "skip_vanilla" lists vanilla-only entries to leave out.

Standard library only (Python 3.8+), runs on Windows too.
Exit codes: 0 ok, 1 check/verification failed, 2 bad input.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

MARK = "added by merge_mapclusterproto.py"


# ---------------------------------------------------------------- parsing
@dataclass
class Entry:
    kind: str          # "export" or "cluster"
    name: str
    first: int         # first line index (0-based, inclusive)
    last: int          # last line index (inclusive)
    canon: tuple       # normalised content, for comparing

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.name}"


@dataclass
class ProtoFile:
    path: Path
    raw: bytes
    bom: bool
    newline: str
    lines: list[str]
    entries: dict[str, Entry] = field(default_factory=dict)
    clusters_close: int = -1   # line of the active </clusters>
    last_cluster_end: int = -1  # line of the last active </cluster>
    duplicates: list[str] = field(default_factory=list)

    @property
    def line_count(self) -> int:
        return len(self.lines) - (self.lines[-1] == "")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    def block(self, e: Entry) -> list[str]:
        return self.lines[e.first:e.last + 1]


def canon(el: ET.Element) -> tuple:
    return (el.tag,
            tuple(sorted((k, v.strip()) for k, v in el.attrib.items())),
            tuple(canon(c) for c in el))


def mask_comments(text: str) -> str:
    """Blank out <!-- --> comments, keeping offsets and line breaks."""
    return re.sub(r"<!--.*?-->",
                  lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  text, flags=re.S)


def load(path: Path, raw: bytes | None = None) -> ProtoFile:
    raw = path.read_bytes() if raw is None else raw
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw[3 if bom else 0:].decode("utf-8")
    crlf = text.count("\r\n")
    newline = "\r\n" if crlf and crlf >= text.count("\n") - crlf else "\n"
    pf = ProtoFile(path, raw, bom, newline, text.split(newline))
    try:
        ET.fromstring(raw)
    except ET.ParseError as e:
        raise SystemExit(f"{path}: XML is not well-formed: {e}")

    masked = mask_comments(text)
    starts = [0]
    for ln in pf.lines[:-1]:
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

    def add(kind: str, name: str, a: int, b: int, frag: str) -> None:
        e = Entry(kind, name, line_of(a), line_of(b - 1),
                  canon(ET.fromstring(frag)))
        if e.key in pf.entries:
            pf.duplicates.append(e.key)
        else:
            pf.entries[e.key] = e

    for m in re.finditer(r'<export\b[^>]*?/>', masked):
        n = re.search(r'\bname="([^"]*)"', m.group(0))
        if n:
            add("export", n.group(1), m.start(), m.end(), m.group(0))
    for m in re.finditer(r'<cluster\b[^>]*>.*?</cluster>', masked, flags=re.S):
        n = re.search(r'\bname="([^"]*)"', m.group(0))
        if n:
            add("cluster", n.group(1), m.start(), m.end(), m.group(0))
        pf.last_cluster_end = max(pf.last_cluster_end, line_of(m.end() - 1))
    closes = [m.start() for m in re.finditer(r"</clusters>", masked)]
    if closes:
        pf.clusters_close = line_of(closes[-1])
    return pf


def names(pf: ProtoFile, kind: str) -> set[str]:
    return {e.name for e in pf.entries.values() if e.kind == kind}


def orphans(pf: ProtoFile) -> tuple[list[str], list[str]]:
    ex, cl = names(pf, "export"), names(pf, "cluster")
    return sorted(cl - ex), sorted(ex - cl)


# ----------------------------------------------------------------- merging
@dataclass
class Result:
    output: bytes
    report: str
    problems: list[str]
    undecided: list[str]


def indent_of(line: str) -> str:
    return line[:len(line) - len(line.lstrip())]


def merge(cfg_path: Path) -> Result:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    here = cfg_path.parent
    mp = load(here / cfg["map"])
    va = load(here / cfg["vanilla"])
    map_label = cfg.get("map_label", "map")
    van_label = cfg.get("vanilla_label", "vanilla")
    decisions: dict = cfg.get("decisions", {})
    skip = set(cfg.get("skip_vanilla", []))
    problems: list[str] = []

    for pf in (mp, va):
        if pf.duplicates:
            problems.append(f"{pf.path.name}: defined twice: {pf.duplicates}")
        if pf.clusters_close < 0 or pf.last_cluster_end < 0:
            raise SystemExit(f"{pf.path}: no active <clusters> or <cluster> found")

    only_van = [k for k in va.entries if k not in mp.entries]
    only_map = [k for k in mp.entries if k not in va.entries]
    conflicts = [k for k in mp.entries
                 if k in va.entries and mp.entries[k].canon != va.entries[k].canon]
    added = [k for k in only_van if k not in skip]
    for k in decisions:
        if decisions[k].get("keep") not in ("map", "vanilla"):
            raise SystemExit(f"merge.json: {k} keep must be 'map' or 'vanilla'")
    undecided = [k for k in conflicts if k not in decisions]
    use_vanilla = [k for k in conflicts
                   if decisions.get(k, {}).get("keep") == "vanilla"]
    stale = [k for k in decisions if k not in conflicts]
    stale_skip = [k for k in skip if k not in only_van]

    # Build the new line list. Replacements and insertions are keyed on map
    # line numbers, so the map's own lines never move relative to each other.
    replace = {mp.entries[k].first: k for k in use_vanilla}
    skip_lines: set[int] = set()
    for k in use_vanilla:
        e = mp.entries[k]
        skip_lines.update(range(e.first + 1, e.last + 1))

    def tagged(kind: str, ref_line: str) -> list[str]:
        keys = [k for k in added if k.startswith(kind + ":")]
        if not keys:
            return []
        ind = indent_of(ref_line) or "\t\t"
        out = [f"{ind}<!-- {MARK}: from {van_label} -->"]
        for k in keys:
            out += va.block(va.entries[k])
        out.append(f"{ind}<!-- end of {MARK} block -->")
        return out

    first_export = min((e.first for e in mp.entries.values() if e.kind == "export"),
                       default=mp.clusters_close)
    first_cluster = min(e.first for e in mp.entries.values() if e.kind == "cluster")
    export_block = tagged("export", mp.lines[first_export])
    cluster_block = tagged("cluster", mp.lines[first_cluster])

    out: list[str] = []
    for i, line in enumerate(mp.lines):
        if i == mp.clusters_close:
            out += export_block
        if i in replace:
            k = replace[i]
            out.append(f"{indent_of(line)}<!-- {MARK}: vanilla version kept "
                       f"for {k} (decision in merge.json) -->")
            out += va.block(va.entries[k])
            continue
        if i in skip_lines:
            continue
        out.append(line)
        if i == mp.last_cluster_end:
            out += cluster_block

    text = mp.newline.join(out)
    data = (b"\xef\xbb\xbf" if mp.bom else b"") + text.encode("utf-8")

    # ------------------------------------------------------- verification
    try:
        ET.fromstring(data)
    except ET.ParseError as e:
        problems.append(f"master is not well-formed XML: {e}")
    else:
        ms = load(Path(cfg["output"]), data)
        want = set(mp.entries) | set(added)
        if set(ms.entries) != want:
            problems.append(f"master entries differ from expected: missing "
                            f"{sorted(want - set(ms.entries))}, extra "
                            f"{sorted(set(ms.entries) - want)}")
        if ms.duplicates:
            problems.append(f"master defines twice: {ms.duplicates}")
        for k in ms.entries:
            src = va if (k in added or k in use_vanilla) else mp
            if k in src.entries and ms.entries[k].canon != src.entries[k].canon:
                problems.append(f"master {k} does not match its source")
        if ms.newline != mp.newline or ms.bom != mp.bom:
            problems.append("master line endings/BOM differ from the map file")
    # every map line kept, in order, apart from replaced blocks
    kept = [l for i, l in enumerate(mp.lines)
            if i not in skip_lines and i not in replace]
    it = iter(out)
    if not all(any(l == o for o in it) for l in kept):
        problems.append("some of the map's own lines are missing from the master")

    # ---------------------------------------------------------------- report
    m_or, m_ex = orphans(mp)
    rel = lambda p: Path(p).as_posix()
    r = [f"# mapclusterproto.xml merge report", "",
         "Generated by `tools/merge_mapclusterproto.py`. Do not edit by hand.", "",
         "| | File | sha256 | Lines | Exports | Clusters |",
         "|---|---|---|---|---|---|"]
    for label, pf, p in ((map_label, mp, cfg["map"]), (van_label, va, cfg["vanilla"])):
        r.append(f"| {label} | `{rel(p)}` | `{pf.sha256[:12]}` | {pf.line_count} "
                 f"| {len(names(pf, 'export'))} | {len(names(pf, 'cluster'))} |")
    r.append(f"| **Master** | `{rel(cfg['output'])}` | "
             f"`{hashlib.sha256(data).hexdigest()[:12]}` | {len(out) - (out[-1] == "")} | | |")
    r += ["", f"Line endings: {'CRLF' if mp.newline == chr(13)+chr(10) else 'LF'}"
          f" (same as the map file). Verification: "
          f"{'**FAILED**' if problems else 'passed'}.", ""]
    if problems:
        r += ["## Problems", ""] + [f"- {p}" for p in problems] + [""]

    def lst(keys: list[str]) -> str:
        return ", ".join(f"`{k}`" for k in keys) if keys else "none"

    r += ["## Conflicts (same name, different content)", ""]
    if conflicts:
        r += ["| Entry | Kept | Why |", "|---|---|---|"]
        for k in conflicts:
            d = decisions.get(k)
            kept_from = d["keep"] if d else "map (**undecided**, waiting on Boss)"
            r.append(f"| `{k}` | {kept_from} | {d.get('why', '') if d else ''} |")
        r += ["", "Differences:", ""]
        for k in conflicts:
            r += [f"<details><summary><code>{k}</code></summary>", "", "```xml",
                  f"<!-- {map_label} -->"] + mp.block(mp.entries[k]) + \
                 [f"<!-- {van_label} -->"] + va.block(va.entries[k]) + \
                 ["```", "", "</details>", ""]
    else:
        r += ["none", ""]
    r += ["## Added from vanilla", "", lst(added), "",
          "## Vanilla-only entries left out (skip_vanilla)", "",
          lst(sorted(skip & set(only_van))), "",
          f"## Only in the map file (kept): {len(only_map)}", "", lst(only_map), "",
          "## Notes", "",
          f"- Map clusters with no export (no model to attach to): {lst(m_or)}",
          f"- Map exports with no cluster: {lst(m_ex)}"]
    if undecided:
        r.append(f"- **Undecided conflicts:** {lst(undecided)}. Add a decision to "
                 f"merge.json, then rebuild.")
    if stale:
        r.append(f"- Decisions for entries that no longer conflict (safe to "
                 f"remove from merge.json): {lst(stale)}")
    if stale_skip:
        r.append(f"- skip_vanilla entries that are no longer vanilla-only: "
                 f"{lst(stale_skip)}")
    r.append("")
    return Result(data, "\n".join(r), problems, undecided)


# ------------------------------------------------------------------- diff
def diff(old: Path, new: Path, old_raw: bytes | None = None) -> int:
    a, b = load(old, old_raw), load(new)
    print(f"old: {old}  sha256 {a.sha256[:12]}  {a.line_count} lines")
    print(f"new: {new}  sha256 {b.sha256[:12]}  {b.line_count} lines")
    if a.raw == b.raw:
        print("identical")
        return 0
    if a.newline != b.newline:
        print(f"line endings changed: {a.newline!r} -> {b.newline!r}")
    for kind in ("export", "cluster"):
        ka = {k for k in a.entries if k.startswith(kind)}
        kb = {k for k in b.entries if k.startswith(kind)}
        changed = sorted(k for k in ka & kb if a.entries[k].canon != b.entries[k].canon)
        print(f"== {kind}s: {len(ka)} -> {len(kb)}")
        print(f"  removed: {sorted(ka - kb)}")
        print(f"  added:   {sorted(kb - ka)}")
        print(f"  changed: {changed}")
    for label, pf in (("old", a), ("new", b)):
        o, e = orphans(pf)
        if o or e:
            print(f"{label}: clusters with no export {o}; exports with no cluster {e}")
    return 0


# -------------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("build", "check", "diff"):
        print(__doc__)
        return 2
    if argv[0] == "diff":
        return diff(Path(argv[1]), Path(argv[2]))

    cfg_path = Path(argv[1]).resolve()
    strict = "--strict" in argv
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    res = merge(cfg_path)
    out_path = cfg_path.parent / cfg["output"]
    rep_path = cfg_path.parent / cfg.get("report", "MERGE_REPORT.md")
    for p in res.problems:
        print(f"ERROR {p}")
    for k in res.undecided:
        print(f"UNDECIDED {k}: map version kept for now")

    if argv[0] == "build":
        if res.problems:
            print("Not written: fix the problems above first.")
            return 1
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(res.output)
        rep_path.write_text(res.report, encoding="utf-8", newline="\n")
        print(f"wrote {out_path} and {rep_path}")
    else:
        stale = [p for p, want in ((out_path, res.output),
                                   (rep_path, res.report.encode("utf-8")))
                 if not p.is_file() or p.read_bytes() != want]
        for p in stale:
            print(f"ERROR {p} is out of date: run 'build' and commit")
        if stale or res.problems:
            return 1
        print(f"{out_path.name} is up to date")
    return 1 if (strict and res.undecided) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
