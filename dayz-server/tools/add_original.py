#!/usr/bin/env python3
"""Store a new version of an original (map author, mod or Bohemia) file.

The file is copied byte for byte into dayz-server/originals/<source>/,
replacing the previous version (git keeps every version), a row is added to
that folder's VERSIONS.md, and the change from the previous version is
printed so it can be reviewed before committing.

Usage:
    python3 tools/add_original.py <source> <file> [--note "where it came from"]

Example:
    python3 tools/add_original.py sahrani-plus D:/upload/mapclusterproto.xml \
        --note "Sahrani Plus workshop update, 2026-12-01"

Then rebuild any merge that uses it and commit both together:
    python3 tools/merge_mapclusterproto.py build sahrani-plus/merge.json
"""
from __future__ import annotations

import difflib
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = ("| Date | File | sha256 | Lines | Line endings | Note |\n"
          "|---|---|---|---|---|---|\n")


def describe(raw: bytes) -> tuple[int, str]:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    ending = "CRLF" if crlf and crlf == lf else ("LF" if not crlf else "mixed")
    lines = lf + (0 if raw.endswith(b"\n") or not raw else 1)
    return lines, ending


def well_formed(path: Path, raw: bytes) -> str | None:
    suffix = path.suffix.lower()
    try:
        if suffix == ".xml":
            ET.fromstring(raw)
        elif suffix == ".json":
            json.loads(raw.decode("utf-8-sig"))
    except (ET.ParseError, ValueError) as e:
        return str(e)
    return None


def main(argv: list[str]) -> int:
    note = ""
    if "--note" in argv:
        i = argv.index("--note")
        note = argv[i + 1] if i + 1 < len(argv) else ""
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    source, src = argv[0], Path(argv[1])
    if not src.is_file():
        print(f"Not a file: {src}")
        return 2

    raw = src.read_bytes()
    dest_dir = ROOT / "originals" / source
    dest = dest_dir / src.name
    old = dest.read_bytes() if dest.is_file() else None
    if old == raw:
        print(f"{dest} already holds this exact version; nothing to do.")
        return 0

    problem = well_formed(src, raw)
    if problem:
        # Originals are stored as-is even when broken, so the record is true
        # to what was received; the merge and validator will refuse it.
        print(f"WARNING: {src.name} is not well-formed: {problem}")

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    lines, ending = describe(raw)
    sha = hashlib.sha256(raw).hexdigest()
    log = dest_dir / "VERSIONS.md"
    text = log.read_text(encoding="utf-8") if log.is_file() else \
        f"# Originals: {source}\n\nEvery version received, newest last. " \
        f"Files are stored exactly as received; git history holds the " \
        f"older versions.\n\n" + HEADER
    note = note.replace("|", "/")
    text += f"| {date.today().isoformat()} | `{src.name}` | `{sha[:12]}` | " \
            f"{lines} | {ending} | {note} |\n"
    log.write_text(text, encoding="utf-8", newline="\n")
    print(f"stored {dest.relative_to(ROOT)}  sha256 {sha[:12]}  {lines} lines {ending}")

    if old is None:
        print("first version of this file")
        return 0
    if src.name.lower() == "mapclusterproto.xml" and not problem:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import merge_mapclusterproto as m
        m.diff(Path("previous version"), dest, old)
    else:
        a = old.decode("utf-8", "replace").splitlines()
        b = raw.decode("utf-8", "replace").splitlines()
        d = list(difflib.unified_diff(a, b, "previous", "new", lineterm="", n=1))
        print("\n".join(d[:200]))
        if len(d) > 200:
            print(f"... {len(d) - 200} more diff lines (use git diff)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
