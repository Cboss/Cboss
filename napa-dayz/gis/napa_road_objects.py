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
         "asf1_12";X;Y;yaw;pitch;roll;scale;relative height;underground flag;
     load it with File > Import > Objects (the Roads template library must be loaded)

Part geometry comes from roadgen/road_parts_<family>.csv (measured from Bohemia's p3d files
with roadgen/mlod.py): begin centre at (0,0), driving along +Z, curves turn right.
A curve turns left by being laid backwards, which is how the Road Tool uses them too.

The game sets a road part on the ground by its corner points, so parts are written flat
(pitch 0) and need no slope. Needs only plain Python. --dem (GDAL) is optional but
recommended once the road bed is graded (napa_road_bed.py): straights are then only laid
where the ground does not rise through them.
"""

import argparse
import bisect
import csv
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BEAM = 10             # partial roads kept per stretch
BUCKET = 5.0          # length of a stretch (metres)
MAX_LATERAL = 4.0     # a part's end may never sit further than this off the OSM line (metres)
MAX_HEADING = 25.0    # ... or point further than this away from it (degrees)
ANGLE_WEIGHT = 0.5    # one degree of heading error costs as much as this many metres off line
PART_COST = 1.0       # small cost per part: prefer fewer, longer parts
KINK_COST = 4.0       # extra cost for a part that turns 5 degrees or more
SKIP_SUFFIXES = ()        # part name endings to leave out, e.g. ("_12",)
LINK_FAMILY = "asf3"   # on/off ramps (OSM *_link) use this 7 m family whatever road they belong to
JOIN_MAX_BEND = 30.0   # two OSM lines are one road if they meet within this many degrees of straight
END_GAP = 0.75        # a road may stop this far short of its end (metres)
END_OVER = 7.0        # ... or run this far past it
END_WEIGHT = 20.0     # how much being off line at the very end costs (keeps junctions tidy)
SAG_TOL = 0.05        # with --dem: ground may rise this far above a straight part between its ends (metres)
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
        lo = max(1, bisect.bisect_left(self.s, s_from - 5))
        hi = min(len(self.p), bisect.bisect_right(self.s, s_from + window) + 1)
        for i in range(lo, hi):
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
            if name.endswith(SKIP_SUFFIXES):
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


def walk(line, parts, short, terrain=None):
    """Lay parts along one line with a beam search and return (part, yaw, origin) tuples.

    Every partial road is scored by how far and how crooked it runs from the OSM line; the
    best few per stretch of road are kept and extended. Looking ahead like this avoids the
    left-right wobble a one-part-at-a-time choice makes on gentle curves, where the part
    set has nothing between a 1000 m and a 100 m radius.
    """
    goal = line.length
    a, b = line.p[-2], line.p[-1]                            # run-off past the end, so the last
    k = (END_OVER + 30) / (math.dist(a, b) or 1e-9)          # part may overshoot instead of stopping short
    line = Line(line.p + [(b[0] + (b[0] - a[0]) * k, b[1] + (b[1] - a[1]) * k)])
    pos, hdg = line.at(0)
    start = (0.0, 0.0, pos, hdg, None, None)        # cost, chainage, pos, heading, parent, (part, yaw, origin)
    buckets = {0: [start]}
    done = None
    b = 0
    last = int((goal + END_OVER) / BUCKET) + 3
    while b <= last:
        states = buckets.pop(b, None)
        b += 1
        if not states:
            continue
        states.sort(key=lambda q: q[0])
        seen, keep = set(), []
        for st in states:
            k = (round(st[2][0] * 2), round(st[2][1] * 2), round(st[3]))
            if k not in seen:
                seen.add(k)
                keep.append(st)
                if len(keep) >= BEAM:
                    break
        for st in keep:
            cost, s0, pos, hdg = st[0], st[1], st[2], st[3]
            if s0 >= goal - END_GAP:                           # reached the end
                lat = line.project(pos, s0)[1]
                ang = abs(angdiff(hdg, line.at(s0)[1]))
                cost += END_WEIGHT * (lat * lat + (ang * ANGLE_WEIGHT) ** 2) + (s0 - goal) ** 2
                if done is None or cost < done[0]:
                    done = (cost,) + st[1:]
                continue
            for part in parts:
                if s0 + part["length"] > goal + END_OVER:
                    continue
                yaw, origin, end, nh = lay(part, pos, hdg)
                ns, lat = line.project(end, s0)
                if ns <= s0 + 1 or lat > MAX_LATERAL:
                    continue
                ang = abs(angdiff(nh, line.at(ns)[1]))
                if ang > MAX_HEADING:
                    continue
                c = cost + part["length"] * (lat * lat + (ang * ANGLE_WEIGHT) ** 2) + PART_COST
                if abs(part["turn"]) >= 5:
                    c += KINK_COST
                if terrain is not None and part["turn"] == 0 and pokes_through(terrain, part, yaw, origin):
                    continue
                nb = max(b, int(ns / BUCKET))
                buckets.setdefault(nb, []).append((c, ns, end, nh, st, (part, yaw, origin)))
    if done is None:                                           # could not reach the end: keep the furthest
        return walk_greedy(line, parts, short)
    placed = []
    st = done
    while st[5] is not None:
        placed.append(st[5])
        st = st[4]
    return placed[::-1]


def walk_greedy(line, parts, short):
    """Fallback: one part at a time, always the one that ends closest to the line."""
    placed = []
    pos, hdg = line.at(0)
    s = 0.0
    while line.length - s > short["length"] * 0.5 and len(placed) < 100000:
        best, best_cost = None, 1e18
        for part in parts:
            if s + part["length"] > line.length + 2:
                continue
            yaw, origin, end, nh = lay(part, pos, hdg)
            ns, lat = line.project(end, s)
            if ns <= s:
                continue
            ang = abs(angdiff(nh, line.at(ns)[1]))
            cost = lat * lat + (ang * ANGLE_WEIGHT) ** 2 - 0.02 * part["length"]
            if cost < best_cost:
                best_cost, best = cost, (part, yaw, origin, end, nh, ns)
        if best is None:
            break
        part, yaw, origin, pos, hdg, s = best
        placed.append((part, yaw, origin))
    return placed


# ---------------------------------------------------------------- joining OSM pieces
def join_lines(lines):
    """Join polylines that continue each other.

    At every node the line ends are paired off straightest-first, so a highway carries on
    through the point where a ramp leaves it, and two ramps that merely touch at a sharp
    angle stay separate roads.
    """
    key = lambda q: (round(q[0] / SNAP), round(q[1] / SNAP))

    def outward(i, e):
        """Heading pointing away from the node along line i at its end e (0 start, 1 end)."""
        pts = lines[i]
        a, b = (pts[0], pts[1]) if e == 0 else (pts[-1], pts[-2])
        return heading(b[0] - a[0], b[1] - a[1])

    nodes = {}
    for i, pts in enumerate(lines):
        nodes.setdefault(key(pts[0]), []).append((i, 0))
        nodes.setdefault(key(pts[-1]), []).append((i, 1))
    partner = {}
    for ends in nodes.values():
        pairs = []
        for x in range(len(ends)):
            for y in range(x + 1, len(ends)):
                if ends[x][0] == ends[y][0]:
                    continue
                bend = abs(angdiff(outward(*ends[x]), outward(*ends[y]) + 180))
                if bend <= JOIN_MAX_BEND:
                    pairs.append((bend, ends[x], ends[y]))
        for bend, p, q in sorted(pairs):
            if p not in partner and q not in partner:
                partner[p], partner[q] = q, p

    used, chains = set(), []
    for i in range(len(lines)):
        if i in used:
            continue
        used.add(i)
        chain = list(lines[i])
        tip = (i, 1)                                       # grow forward from the end
        while tip in partner and partner[tip][0] not in used:
            j, e = partner[tip]
            used.add(j)
            chain += (lines[j] if e == 0 else lines[j][::-1])[1:]
            tip = (j, 1 - e)
        tip = (i, 0)                                       # then backward from the start
        while tip in partner and partner[tip][0] not in used:
            j, e = partner[tip]
            used.add(j)
            chain = (lines[j] if e == 1 else lines[j][::-1])[:-1] + chain
            tip = (j, 1 - e)
        chains.append(chain)
    return chains


# ---------------------------------------------------------------- terrain (optional)
class Terrain:
    """In-game heights the way the game holds them: value [row, col] is the ground at the
    grid point x = col * cell, z = (rows - 1 - row) * cell (x measured from the map's west edge)."""

    def __init__(self, path):
        import array
        import numpy
        if path.lower().endswith(".npy"):
            a = numpy.load(path)
        else:
            from osgeo import gdal
            gdal.UseExceptions()
            ds = gdal.Open(path)                    # keep the dataset alive while its band is read
            a = ds.GetRasterBand(1).ReadAsArray()
            ds = None
        self.n = a.shape[0]
        self.cell = 20480.0 / self.n
        self.flat = array.array("f")                # compact, and fast for single lookups
        self.flat.frombytes(numpy.ascontiguousarray(a, dtype=numpy.float32).tobytes())

    def h(self, x, y):
        n = self.n
        c = (x - 200000.0) / self.cell
        r = (n - 1) - y / self.cell
        c0 = int(c) if c > 0 else 0
        r0 = int(r) if r > 0 else 0
        if c0 > n - 2:
            c0 = n - 2
        if r0 > n - 2:
            r0 = n - 2
        tc, tr = min(1.0, max(0.0, c - c0)), min(1.0, max(0.0, r - r0))
        f, k = self.flat, r0 * n + c0
        return (f[k] * (1 - tc) + f[k + 1] * tc) * (1 - tr) + (f[k + n] * (1 - tc) + f[k + n + 1] * tc) * tr


def pokes_through(terrain, part, yaw, origin):
    """True if the ground rises through a straight part between its corners. The game sets a
    road part on the ground by its corner points only, so a straight is a flat sheet between
    its two ends; curves have a row of points every couple of metres and follow the ground."""
    w = part["width"] / 2
    for lat in (-w, 0.0, w):
        h0 = terrain.h(*local_to_world(origin[0], origin[1], yaw, lat, 0.0))
        h1 = terrain.h(*local_to_world(origin[0], origin[1], yaw, lat, part["ez"]))
        steps = max(2, int(part["ez"] / 3.0))
        for k in range(1, steps):
            t = k / steps
            g = terrain.h(*local_to_world(origin[0], origin[1], yaw, lat, part["ez"] * t))
            if g - (h0 + (h1 - h0) * t) > SAG_TOL:
                return True
    return False


def write_line(f, part, origin, yaw, pivot, yaw_dir, pitch=0.0):
    if pivot == "bbox":
        px, py = local_to_world(origin[0], origin[1], yaw, *part["bbox"])
    else:
        px, py = origin
    y = yaw if yaw_dir == "cw" else (360 - yaw) % 360
    f.write(f'"{part["name"]}";{px:.3f};{py:.3f};{y:.4f};{pitch:.4f};0.0000;1.0000;0.000;0;\n')


def write_test(parts, at, out):
    """Four rows of the same chain (straight, right curve, straight, left curve, straight),
    60 m apart, each with one guess of pivot and yaw direction. The row whose pieces join
    up cleanly in Terrain Builder tells us which settings are right."""
    pick = {(q["name"], q["dir"]): q for q in parts}
    chain = [pick[("asf1_25", 1)], pick[("asf1_30 25", 1)], pick[("asf1_25", 1)],
             pick[("asf1_30 25", -1)], pick[("asf1_25", 1)], pick[("asf1_12", 1)]]
    rows = [("A", "bbox", "cw"), ("B", "origin", "cw"), ("C", "bbox", "ccw"), ("D", "origin", "ccw")]
    with open(out, "w", newline="\r\n") as f:
        for k, (label, pivot, yaw_dir) in enumerate(rows):
            pos, hdg = (at[0] + 60 * k, at[1]), 0.0
            for part in chain:
                yaw, origin, pos, hdg = lay(part, pos, hdg)
                write_line(f, part, origin, yaw, pivot, yaw_dir)
            print(f"  row {label} at X {at[0] + 60 * k:.0f}: pivot {pivot}, yaw {yaw_dir}")
    print(f"Wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    guide = r"D:\NapaMap\gis\full\roads_guide\napa_roads_guide"
    if not os.path.exists(guide + ".shp"):
        guide = os.path.join(HERE, "..", "terrain", "napa", "roads_guide", "napa_roads_guide")
    ap.add_argument("--guide", default=guide,
                    help="road guide shapefile without .shp")
    ap.add_argument("--family", default="asf1")
    ap.add_argument("--highway", nargs="+", help="only these OSM highway types, e.g. motorway_link trunk_link")
    ap.add_argument("--ref", help="only roads with this ref, e.g. 29")
    ap.add_argument("--box", nargs=4, type=float, metavar=("X1", "Y1", "X2", "Y2"),
                    help="only roads inside this Terrain Builder box (for a test patch)")
    ap.add_argument("--dem", help="in-game height GeoTIFF (full_dem_roads.tif): straights are only laid "
                                  "where the ground does not rise through them")
    ap.add_argument("--pivot", choices=("bbox", "origin"), default="bbox",
                    help="where Terrain Builder puts an object's position: its bounding box centre "
                         "(default) or the model origin")
    ap.add_argument("--yaw", choices=("cw", "ccw"), default="cw",
                    help="Terrain Builder yaw direction: clockwise (default) or counter-clockwise")
    ap.add_argument("--test", nargs=2, type=float, metavar=("X", "Y"),
                    help="write the 4-row placement test at this map position and stop")
    ap.add_argument("--out")
    args = ap.parse_args()

    parts = load_parts(args.family)
    if args.test:
        return write_test(parts, args.test, args.out or "road_test.txt")
    short = min(parts, key=lambda q: q["length"] if q["turn"] == 0 else 1e9)
    terrain = Terrain(args.dem) if args.dem else None

    lines = []
    for shapes, rec in read_shapefile(args.guide):
        hw = rec.get("highway", "")
        fam = LINK_FAMILY if hw.endswith("_link") else rec.get("family")   # ramps are one lane
        if fam != args.family or (args.highway and hw not in args.highway):
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

    chains = join_lines(lines)
    out_path = args.out or os.path.join(os.getcwd(), f"napa_roads_{args.family}.txt")
    total_parts, total_len = 0, 0.0
    counts = {}
    with open(out_path, "w", newline="\r\n") as f:
        for pts in chains:
            line = Line(pts)
            if line.length < short["length"]:
                continue
            for part, yaw, origin in walk(line, parts, short, terrain):
                write_line(f, part, origin, yaw, args.pivot, args.yaw)
                total_parts += 1
                total_len += part["length"]
                counts[part["name"]] = counts.get(part["name"], 0) + 1
    print(f"Wrote {out_path}")
    print(f"  {len(chains)} roads, {total_parts} parts, {total_len / 1000:.1f} km")
    for n, c in sorted(counts.items(), key=lambda kv: -kv[1])[:12]:
        print(f"    {c:6d}  {n}")


if __name__ == "__main__":
    sys.exit(main())
