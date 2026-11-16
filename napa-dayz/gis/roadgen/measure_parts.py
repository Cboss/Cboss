"""
Measure Bohemia's DayZ road parts and write road_parts_<family>.csv for napa_road_objects.py.

    python measure_parts.py <folder with the .p3d road parts> [output folder]

For every part with the four memory points LB/PB (begin left/right) and LE/PE (end left/right):
width, where the end centre sits and how far the part turns (begin centre = 0,0, road along +Z,
+ = turns right), and the bounding-box centre Terrain Builder uses as the object's position.
"""
import csv
import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mlod import parse


def measure(path):
    lods = parse(path)
    mem = [l for l in lods if 9e14 < l["res"] < 2e15]
    if not mem or not all(k in mem[0]["tags"] for k in ("LB", "PB", "LE", "PE")):
        return None
    t, P = mem[0]["tags"], mem[0]["pts"]
    lb, pb, le, pe = (P[t[k][0]] for k in ("LB", "PB", "LE", "PE"))
    bx, bz = (lb[0] + pb[0]) / 2, (lb[2] + pb[2]) / 2          # begin centre (normally 0,0)
    V = [p for l in lods if l["res"] < 1000 for p in l["pts"]]
    return dict(part=os.path.basename(path)[:-4],
                width=round(math.hypot(pb[0] - lb[0], pb[2] - lb[2]), 3),
                end_x=round((le[0] + pe[0]) / 2 - bx, 3), end_z=round((le[2] + pe[2]) / 2 - bz, 3),
                turn_deg=round(math.degrees(math.atan2(-(pe[2] - le[2]), pe[0] - le[0])), 3),
                bbox_cx=round((min(p[0] for p in V) + max(p[0] for p in V)) / 2 - bx, 3),
                bbox_cz=round((min(p[2] for p in V) + max(p[2] for p in V)) / 2 - bz, 3))


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    fam = {}
    for f in sorted(glob.glob(os.path.join(src, "*.p3d"))):
        name = os.path.basename(f)
        if name.startswith("kr_"):
            continue
        r = measure(f)
        if r:
            fam.setdefault(name.split("_")[0], []).append(r)
    for k, rows in fam.items():
        with open(os.path.join(out, f"road_parts_{k}.csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"{k}: {len(rows)} parts, width {rows[0]['width']} m")


if __name__ == "__main__":
    main()
