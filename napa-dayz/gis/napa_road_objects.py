"""
Napa DayZ map: lay DayZ road parts along the OSM road guide (Phase 4c, "Plan B").

    python napa_road_objects.py --family asf1 [--ref 29] [--box X1 Y1 X2 Y2] [--dem full_dem_water.tif]
                                [--pivot bbox|origin] [--out napa_roads_asf1.txt]

Terrain Builder's Road Tool would not let us draw roads ("target layer is locked"), and in the
end DayZ only sees roads as ordinary objects anyway. So this script does the Road Tool's job:

  1. reads roads_guide/napa_roads_guide.shp (Terrain Builder coordinates, made by
     napa_roads_guide.py) and joins OSM pieces that simply continue each other
  2. walks each road like a turtle, choosing at every step the longest road part (straight
     25 / 12.5 / 6.25 m, or a curve, turned left or right) that stays on the OSM line
  3. writes one line per part in Terrain Builder's object text format:
         "asf1_12";X;Y;yaw;pitch;roll;scale;relative height;
     load it with File > Import > Objects (the Roads template library must be loaded)

Part geometry comes from roadgen/road_parts_<family>.csv (measured from Bohemia's p3d files
with roadgen/mlod.py): begin centre at (0,0), driving along +Z, curves turn right.
A curve turns left by being laid backwards, which is how the Road Tool uses them too.

Needs only plain Python. --dem (GDAL) is optional: with it each part is pitched to the slope.
"""

import argparse
import csv
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LATERAL_TOL = 0.6     # metres a part's end may sit off the OSM line
HEADING_TOL = 3.0     # degrees a part's end may point away from the OSM line
SNAP = 1.0            # road ends closer than this are the same node (metres)


# ---------------------------------------------------------------- shapefile (no GDAL needed)
def read_shapefile(base):
    """Polylines and attributes from base.shp / base.dbf."""
    with open(base + ".dbf", "rb") as f:
        dbf = f.read()
    nrec, hlen, rlen = struct.unpack("<IHH", dbf[4:12])
    fields, p = [], 32
    while dbf[p] != 0x0D:
        name = dbf[p:p + 11].split(b"\0")[0].decode()
        fields.append((name, dbf[p + 16]))
        p += 32
    recs = []
    for i in range(nrec):
        r = dbf[hlen + i * rlen + 1: hlen + (i + 1) * rlen]
        d, q = {}, 0
        for name, ln in fields:
            d[name] = r[q:q + ln].decode("utf-8", "replace").strip()
            q += ln
        recs.append(d)

    with open(base + ".shp", "rb") as f:
        shp = f.read()
    out, p = [], 100
    while p < len(shp):
        clen = struct.unpack(">I", shp[p + 4:p + 8])[0] * 2
        c = shp[p + 8:p + 8 + clen]
        p += 8 + clen
        if struct.unpack("<i", c[:4])[0] not in (3, 13, 23):
            out.append([])
            continue
        nparts, npts = struct.unpack("<ii", c[36:44])
        starts = list(struct.unpack(f"<{nparts}i", c[44:44 + 4 * nparts])) + [npts]
        xy = struct.unpack(f"<{2 * npts}d", c[44 + 4 * nparts: 44 + 4 * nparts + 16 * npts])
        pts = [(xy[2 * k], xy[2 * k + 1]) for k in range(npts)]
        out.append([pts[starts[k]:starts[k + 1]] for k in range(nparts)])
    return [(parts, recs[i]) for i, parts in enumerate(out)]


# ---------------------------------------------------------------- geometry helpers
def heading(dx, dy):
    """Compass heading in degrees, clockwise from north (+Y)."""
    return math.degrees(math.atan2(dx, dy)) % 360


def angdiff(a, b):
    return (a - b + 180) % 360 - 180


def local_to_world(px, py, yaw, x, z):
    """Part-local (x right, z forward) to map coordinates for a part at (px,py) facing yaw."""
    r = math.radians(yaw)
    return px + x * math.cos(r) + z * math.sin(r), py - x * math.sin(r) + z * math.cos(r)


class Line:
    """A polyline with chainage, nearest-point and tangent queries."""

    def __init__(self, pts):
        self.p = pts
        self.s = [0.0]
        for a, b in zip(pts, pts[1:]):
            self.s.append(self.s[-1] + math.dist(a, b))
        self.length = self.s[-1]

    def at(self, s):
        s = max(0.0, min(self.length, s))
        for i in range(1, len(self.p)):
            if self.s[i] >= s:
                a, b = self.p[i - 1], self.p[i]
                seg = self.s[i] - self.s[i - 1] or 1e-9
                t = (s - self.s[i - 1]) / seg
                return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), heading(b[0] - a[0], b[1] - a[1])
        a, b = self.p[-2], self.p[-1]
        return b, heading(b[0] - a[0], b[1] - a[1])

    def project(self, q, s_from, window=80.0):
        """Chainage and distance of the point on the line nearest q, searched near s_from."""
        best = (1e18, s_from)
        for i in range(1, len(self.p)):
            if self.s[i] < s_from - 5 or self.s[i - 1] > s_from + window:
                continue
            a, b = self.p[i - 1], self.p[i]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy or 1e-9
            t = max(0.0, min(1.0, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L2))
            c = (a[0] + t * dx, a[1] + t * dy)
            d = math.dist(c, q)
            if d < best[0]:
                best = (d, self.s[i - 1] + t * math.sqrt(L2))
        return best[1], best[0]


# ---------------------------------------------------------------- road parts
def load_parts(family):
    path = os.path.join(HERE, "roadgen", f"road_parts_{family}.csv")
    parts = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            name = r["part"]
            if "konec" in name or "crosswalk" in name or name.startswith("kr_"):
                continue
            ex, ez, turn = float(r["end_x"]), float(r["end_z"]), float(r["turn_deg"])
            bb = (float(r["bbox_cx"]), float(r["bbox_cz"]))
            parts.append(dict(name=name, ex=ex, ez=ez, turn=turn, bbox=bb, width=float(r["width"]),
                              length=math.hypot(ex, ez), dir=+1))
            if abs(turn) > 0.01:                       # the same curve laid backwards turns left
                parts.append(dict(name=name, ex=ex, ez=ez, turn=turn, bbox=bb, width=float(r["width"]),
                                  length=math.hypot(ex, ez), dir=-1))
    parts.sort(key=lambda q: -q["length"])
    return parts


def lay(part, pos, hdg):
    """Place part so the road continues from pos heading hdg.
    Returns (model yaw, model origin, new pos, new heading)."""
    if part["dir"] > 0:
        yaw = hdg
        origin = pos
        end = local_to_world(pos[0], pos[1], yaw, part["ex"], part["ez"])
        return yaw, origin, end, (hdg + part["turn"]) % 360
    # backwards: the part's END sits at pos, the part points the other way
    yaw = (hdg - part["turn"] - 180) % 360
    r = math.radians(yaw)
    end_w = (part["ex"] * math.cos(r) + part["ez"] * math.sin(r), -part["ex"] * math.sin(r) + part["ez"] * math.cos(r))
    origin = (pos[0] - end_w[0], pos[1] - end_w[1])
    return yaw, origin, origin, (hdg - part["turn"]) % 360


def walk(line, parts, short):
    """Greedy turtle along one line. Returns placed (part, yaw, origin) tuples."""
    placed = []
    pos, hdg = line.at(0)
    s = 0.0
    guard = 0
    while line.length - s > short["length"] * 0.5 and guard < 100000:
        guard += 1
        best, best_cost = None, 1e18
        for part in parts:
            if s + part["length"] > line.length + 2:
                continue
            yaw, origin, end, nh = lay(part, pos, hdg)
            ns, lat = line.project(end, s)
            if ns <= s:
                continue
            ang = abs(angdiff(nh, line.at(ns)[1]))
            if lat <= LATERAL_TOL and ang <= HEADING_TOL:
                best = (part, yaw, origin, end, nh, ns)
                break                                      # longest part that fits
            cost = lat * lat + (ang / 2.0) ** 2 - 0.02 * part["length"]
            if cost < best_cost:
                best_cost, best = cost, (part, yaw, origin, end, nh, ns)
        if best is None:
            break
        part, yaw, origin, pos, hdg, s = best
        placed.append((part, yaw, origin))
    return placed


# ---------------------------------------------------------------- joining OSM pieces
def join_lines(lines):
    """Join polylines that continue each other (exactly two ends meet, same family)."""
    key = lambda q: (round(q[0] / SNAP), round(q[1] / SNAP))
    ends = {}
    for i, pts in enumerate(lines):
        ends.setdefault(key(pts[0]), []).append((i, 0))
        ends.setdefault(key(pts[-1]), []).append((i, 1))
    used, chains = set(), []
    for i in range(len(lines)):
        if i in used:
            continue
        used.add(i)
        chain = list(lines[i])
        for side in (1, 0):                                # grow forward, then backward
            while True:
                tip = chain[-1] if side else chain[0]
                here = ends.get(key(tip), [])
                cand = [(j, e) for j, e in here if j not in used]
                if len(here) != 2 or len(cand) != 1:
                    break
                j, e = cand[0]
                used.add(j)
                if side:                                   # next line must start at tip
                    nxt = lines[j] if e == 0 else lines[j][::-1]
                    chain = chain + nxt[1:]
                else:                                      # previous line must end at tip
                    prv = lines[j] if e == 1 else lines[j][::-1]
                    chain = prv[:-1] + chain
        chains.append(chain)
    degree = {k: len(v) for k, v in ends.items()}
    return chains, degree, key


# ---------------------------------------------------------------- terrain (optional)
class Terrain:
    def __init__(self, path):
        from osgeo import gdal
        ds = gdal.Open(path)
        self.a = ds.GetRasterBand(1).ReadAsArray()
        self.n = self.a.shape[0]
        self.cell = 20480.0 / self.n

    def h(self, x, y):
        c = (x - 200000) / self.cell - 0.5
        r = (20480 - y) / self.cell - 0.5
        c0, r0 = int(max(0, min(self.n - 2, math.floor(c)))), int(max(0, min(self.n - 2, math.floor(r))))
        tc, tr = min(1, max(0, c - c0)), min(1, max(0, r - r0))
        a = self.a
        return float((a[r0, c0] * (1 - tc) + a[r0, c0 + 1] * tc) * (1 - tr) +
                     (a[r0 + 1, c0] * (1 - tc) + a[r0 + 1, c0 + 1] * tc) * tr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    guide = r"D:\NapaMap\gis\full\roads_guide\napa_roads_guide"
    if not os.path.exists(guide + ".shp"):
        guide = os.path.join(HERE, "..", "terrain", "napa", "roads_guide", "napa_roads_guide")
    ap.add_argument("--guide", default=guide,
                    help="road guide shapefile without .shp")
    ap.add_argument("--family", default="asf1")
    ap.add_argument("--ref", help="only roads with this ref, e.g. 29")
    ap.add_argument("--box", nargs=4, type=float, metavar=("X1", "Y1", "X2", "Y2"),
                    help="only roads inside this Terrain Builder box (for a test patch)")
    ap.add_argument("--dem", help="in-game height GeoTIFF (full_dem_water.tif) to pitch parts")
    ap.add_argument("--pivot", choices=("bbox", "origin"), default="bbox",
                    help="where Terrain Builder puts an object's position: its bounding box centre "
                         "(default) or the model origin")
    ap.add_argument("--pitch-sign", type=float, default=1.0)
    ap.add_argument("--out")
    args = ap.parse_args()

    parts = load_parts(args.family)
    short = min(parts, key=lambda q: q["length"] if q["turn"] == 0 else 1e9)
    terrain = Terrain(args.dem) if args.dem else None

    lines = []
    for shapes, rec in read_shapefile(args.guide):
        if rec.get("family") != args.family:
            continue
        if args.ref and args.ref not in rec.get("ref", "").replace(" ", "").split(";") \
                and f"CA{args.ref}" not in rec.get("ref", "").replace(" ", "").split(";"):
            continue
        for pts in shapes:
            if args.box:
                x1, y1, x2, y2 = args.box
                pts = [q for q in pts if x1 <= q[0] <= x2 and y1 <= q[1] <= y2]
            if len(pts) >= 2:
                lines.append(pts)

    chains, degree, key = join_lines(lines)
    out_path = args.out or os.path.join(os.getcwd(), f"napa_roads_{args.family}.txt")
    total_parts, total_len = 0, 0.0
    counts = {}
    with open(out_path, "w", newline="\r\n") as f:
        for pts in chains:
            line = Line(pts)
            if line.length < short["length"]:
                continue
            for part, yaw, origin in walk(line, parts, short):
                if args.pivot == "bbox":
                    px, py = local_to_world(origin[0], origin[1], yaw, *part["bbox"])
                else:
                    px, py = origin
                pitch = 0.0
                if terrain:
                    b = origin
                    e = local_to_world(origin[0], origin[1], yaw, part["ex"], part["ez"])
                    pitch = args.pitch_sign * math.degrees(math.atan2(terrain.h(*e) - terrain.h(*b), part["length"]))
                f.write(f'"{part["name"]}";{px:.3f};{py:.3f};{yaw:.4f};{pitch:.4f};0.0000;1.0000;0.000;\n')
                total_parts += 1
                total_len += part["length"]
                counts[part["name"]] = counts.get(part["name"], 0) + 1
    print(f"Wrote {out_path}")
    print(f"  {len(chains)} roads, {total_parts} parts, {total_len / 1000:.1f} km")
    for n, c in sorted(counts.items(), key=lambda kv: -kv[1])[:12]:
        print(f"    {c:6d}  {n}")


if __name__ == "__main__":
    sys.exit(main())
