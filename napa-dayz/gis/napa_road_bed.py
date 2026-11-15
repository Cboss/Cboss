"""
Napa DayZ map: smooth the ground under the roads (Phase 4c, "road bed").

Run from the OSGeo4W Shell:
    python napa_road_bed.py

Why: DayZ lays a road part on the ground by its corner points only. A 25 m straight has four
corners, so wherever the raw lidar ground has a bump, a ditch, a river bank or the edge of an
overpass in between, the ground pokes through the asphalt and the road shows a hole. Real
roads sit on a graded bed. This script grades one for every road in the guide:

  1. walks each road and reads the ground height along its centre line
  2. carries the road over water on a low causeway and over narrow dips (creeks, the gap
     under a removed bridge deck)
  3. smooths that height profile (a road has no bumps along its length)
  4. flattens the ground across the road to the profile height (a road is level side to
     side), then blends back into the natural ground over the next 10 m

Roads are done biggest first: highways, ramps, main roads, two-lane roads, streets, tracks.
A smaller road meets a bigger one at the bigger road's height (an at-grade crossing), and
never changes the bigger road's bed.

Reads   D:\\NapaMap\\gis\\full\\full_dem_water.tif        (in-game heights after smart water)
        D:\\NapaMap\\gis\\full\\roads_guide\\napa_roads_guide.shp
Writes  D:\\NapaMap\\gis\\full\\full_dem_roads.tif
        D:\\NapaMap\\gis\\full\\napa_dem_roads.asc + .prj  (import into Terrain Builder)

The height grid is treated the way the game does: value [row, col] is the ground height at
the grid point x = col * 5 m, z = (rows - 1 - row) * 5 m.
"""

import argparse
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import napa_road_objects as R                      # shapefile reader, line joiner, LINK_FAMILY

CELL = 5.0            # metres between height grid points
ORIGIN_E = 200000.0   # Terrain Builder easting of the map's west edge
DS = 2.5              # spacing of the points a road profile is read at (metres)
NODE_MARGIN = 5.1     # flat bed reaches this far past the road edge: half a grid diagonal
                      # (3.6 m) + how far a part may sit off the centre line (1.5 m)
BLEND = 10.0          # ... then blends into the natural ground over this distance
WATER_MAX = 0.2       # ground below this is sea-level water (smart water: water <= -0.5, land >= 0.4)
DECK_MIN = 1.5        # a causeway over water is at least this high
ROAD_MIN = 0.6        # no road lower than this
SIDE_EXTRA = 1.5      # a grid point beside the centre line may move this much more than the centre-line limit
PIN_GRADE = 0.15      # steepest ramp where a road rises or drops to meet a bigger road

# name, guide family, ramps?, road width, widest dip bridged, smoothing length (all metres)
# name, guide family, ramps?, road width, widest dip bridged, smoothing length (all metres),
# and how far the bed may be raised above / dug below the natural ground on the centre line
LEVELS = [
    dict(name="highways",       family="asf1", link=False, width=12.0, close=80.0, smooth=60.0, fill=8.0, cut=3.0),
    dict(name="ramps",          family=None,   link=True,  width=7.0,  close=60.0, smooth=40.0, fill=8.0, cut=3.0),
    dict(name="main roads",     family="asf2", link=False, width=9.0,  close=60.0, smooth=40.0, fill=8.0, cut=3.0),
    dict(name="two-lane roads", family="asf3", link=False, width=7.0,  close=40.0, smooth=30.0, fill=6.0, cut=2.5),
    dict(name="streets",        family="city", link=False, width=10.0, close=30.0, smooth=30.0, fill=5.0, cut=2.0),
    dict(name="tracks",         family="grav", link=False, width=6.0,  close=20.0, smooth=20.0, fill=3.0, cut=2.0),
]


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------------------------------------------------------------- height grid helpers
def sample(H, x, z):
    """Ground height at map positions x, z (arrays, metres from the south-west corner)."""
    n = H.shape[0]
    fc = np.clip(x / CELL, 0, n - 1.001)
    fr = np.clip((n - 1) - z / CELL, 0, n - 1.001)
    c0 = np.floor(fc).astype(np.int64)
    r0 = np.floor(fr).astype(np.int64)
    tc, tr = fc - c0, fr - r0
    return ((H[r0, c0] * (1 - tc) + H[r0, c0 + 1] * tc) * (1 - tr) +
            (H[r0 + 1, c0] * (1 - tc) + H[r0 + 1, c0 + 1] * tc) * tr)


def nearest_node(n, x, z):
    c = np.clip(np.rint(x / CELL).astype(np.int64), 0, n - 1)
    r = np.clip((n - 1) - np.rint(z / CELL).astype(np.int64), 0, n - 1)
    return r, c


# ---------------------------------------------------------------- profile along one road
def resample(pts):
    """Points every DS metres along a polyline: x, z arrays."""
    p = np.asarray(pts, dtype=np.float64)
    seg = np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))
    s = np.concatenate(([0.0], np.cumsum(seg)))
    if s[-1] < DS:
        return p[[0, -1], 0], p[[0, -1], 1]
    t = np.linspace(0.0, s[-1], int(math.ceil(s[-1] / DS)) + 1)
    return np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])


def sliding(a, half, fn):
    """Running max or min over a window of 2*half+1 samples (edges repeat)."""
    if half <= 0:
        return a.copy()
    p = np.pad(a, half, mode="edge")
    out = p[half:half + len(a)].copy()
    for k in range(1, half + 1):
        out = fn(out, p[half - k:half - k + len(a)])
        out = fn(out, p[half + k:half + k + len(a)])
    return out


def smooth(a, half):
    """Moving average over 2*half+1 samples, twice (edges repeat)."""
    if half <= 0 or len(a) < 3:
        return a.copy()
    k = np.ones(2 * half + 1) / (2 * half + 1)
    for _ in range(2):
        a = np.convolve(np.pad(a, half, mode="edge"), k, mode="valid")
    return a


def causeways(p):
    """Carry the profile over sea-level water: a straight deck from bank to bank."""
    wet = p < WATER_MAX
    if not wet.any():
        return p, 0.0
    p = p.copy()
    n = len(p)
    k = max(1, int(15.0 / DS))                     # reach 15 m onto each bank
    edges = np.flatnonzero(np.diff(np.concatenate(([0], wet.astype(np.int8), [0]))))
    length = 0.0
    for a, b in zip(edges[0::2], edges[1::2]):     # wet run is samples a .. b-1
        if a == 0 or b == n:                       # the road ends in the water: just keep it dry
            p[a:b] = np.maximum(p[a:b], ROAD_MIN)
            continue
        i0, i1 = max(0, a - k), min(n - 1, b + k - 1)
        left = max(float(p[i0:a].max()), DECK_MIN)
        right = max(float(p[b:i1 + 1].max()), DECK_MIN)
        deck = np.linspace(left, right, i1 - i0 + 1)
        p[i0:i1 + 1] = np.maximum(p[i0:i1 + 1], deck)
        length += (b - a) * DS
    return p, length


def profile(H, x, z, level, pinned, pin_h):
    """Smoothed road-bed height at each sample of one road. `pinned` marks the samples that
    lie on or right beside a bigger road's bed, `pin_h` is that bed's height there."""
    raw = sample(H, x, z)
    p, bridged = causeways(raw)
    half_c = int(round(level["close"] / DS / 2))
    p = sliding(sliding(p, half_c, np.maximum), half_c, np.minimum)     # fill narrow dips
    p = smooth(p, int(round(level["smooth"] / DS / 2)))
    base = np.maximum(causeways(raw)[0], ROAD_MIN)                     # natural ground, dry
    p = smooth(np.clip(p, base - level["cut"], base + level["fill"]), 3)
    p = np.maximum(p, ROAD_MIN)

    if pinned.any():                               # meet bigger roads at their height
        idx = np.arange(len(p)) * (PIN_GRADE * DS)
        hi = np.where(pinned, pin_h, np.inf)       # may not be higher than pin + ramp
        up = np.minimum(np.minimum.accumulate(hi - idx) + idx,
                        (np.minimum.accumulate((hi + idx)[::-1])[::-1]) - idx)
        lo = np.where(pinned, pin_h, -np.inf)      # nor lower than pin - ramp
        dn = np.maximum(np.maximum.accumulate(lo + idx) - idx,
                        (np.maximum.accumulate((lo - idx)[::-1])[::-1]) + idx)
        p = np.clip(p, dn, up)
        free = ~pinned
        if free.any():                             # take the kink out where the ramp starts
            soft = smooth(p, 2)
            p = np.where(free, soft, pin_h)
        else:
            p = pin_h.copy()
    return p, bridged


def pins(H, lock, xs, zs, radius):
    """For every sample: does a bigger road's bed lie within `radius`, and at what height?"""
    n = H.shape[0]
    i0 = np.rint(xs / CELL).astype(np.int64)
    j0 = np.rint(zs / CELL).astype(np.int64)
    wsum = np.zeros(len(xs))
    hsum = np.zeros(len(xs))
    rad = int(math.ceil(radius / CELL))
    for di in range(-rad, rad + 1):
        for dj in range(-rad, rad + 1):
            ii, jj = np.clip(i0 + di, 0, n - 1), np.clip(j0 + dj, 0, n - 1)
            d = np.hypot(ii * CELL - xs, jj * CELL - zs)
            rr = n - 1 - jj
            w = np.where(lock[rr, ii] & (d <= radius), (1.0 - d / (radius + CELL)) ** 2, 0.0)
            wsum += w
            hsum += w * H[rr, ii]
    pinned = wsum > 0
    return pinned, np.where(pinned, hsum / np.maximum(wsum, 1e-12), 0.0)


# ---------------------------------------------------------------- stamping a level into the grid
def stamp(H, lock, xs, zs, ps, core, total):
    """Flatten the grid to the profile heights within `core` of the samples, blending out to
    `total`. Locked points are left alone. Returns (mask of points changed, mask of bed points)."""
    n = H.shape[0]
    i0 = np.rint(xs / CELL).astype(np.int64)
    j0 = np.rint(zs / CELL).astype(np.int64)
    best = np.full(n * n, np.inf, dtype=np.float32)
    wsum = np.zeros(n * n, dtype=np.float64)
    hsum = np.zeros(n * n, dtype=np.float64)
    rad = int(math.ceil(total / CELL)) + 1
    for di in range(-rad, rad + 1):
        for dj in range(-rad, rad + 1):
            if math.hypot(di, dj) * CELL > total + CELL:
                continue
            ii, jj = i0 + di, j0 + dj
            d = np.hypot(ii * CELL - xs, jj * CELL - zs)
            ok = (ii >= 0) & (ii < n) & (jj >= 0) & (jj < n) & (d <= total)
            idx = (n - 1 - jj[ok]) * n + ii[ok]
            d = d[ok]
            np.minimum.at(best, idx, d.astype(np.float32))          # distance to the nearest road
            w = (1.0 - d / total) ** 4                              # nearby samples count most
            np.add.at(wsum, idx, w)
            np.add.at(hsum, idx, w * ps[ok])
    # Each grid point takes the weighted mean of the profile heights around it. Where two
    # roads run side by side (the two carriageways of a highway) or cross, their beds merge
    # smoothly instead of meeting in a step.
    target = (hsum / np.maximum(wsum, 1e-12)).astype(np.float32)
    best = best.reshape(n, n)
    target = target.reshape(n, n)
    touch = np.isfinite(best) & ~lock
    w = np.clip((total - best[touch]) / max(total - core, 1e-6), 0.0, 1.0)
    w = w * w * (3 - 2 * w)                        # smooth step: 1 on the bed, 0 at the outer edge
    w[best[touch] <= core] = 1.0
    old = H[touch]
    H[touch] = (w * target[touch] + (1 - w) * old).astype(H.dtype)
    return touch, (best <= core)


def level_roads(recs, level):
    """Polylines of one level, joined into whole roads."""
    lines = []
    for shapes, rec in recs:
        hw = rec.get("highway", "")
        link = hw.endswith("_link")
        if link != level["link"] or (not link and rec.get("family") != level["family"]):
            continue
        for pts in shapes:
            if len(pts) >= 2:
                lines.append([(x - ORIGIN_E, y) for x, y in pts])
    return R.join_lines(lines) if lines else []


def build(H, recs, levels=LEVELS, quiet=False):
    """Grade road beds into height grid H (changed in place). Returns per-level statistics."""
    n = H.shape[0]
    lock = np.zeros((n, n), dtype=bool)
    before = H.copy()
    stats = []
    for level in levels:
        chains = level_roads(recs, level)
        if not chains:
            continue
        core = level["width"] / 2 + NODE_MARGIN
        samples = [resample(pts) for pts in chains]
        xs = np.concatenate([x for x, _ in samples])
        zs = np.concatenate([z for _, z in samples])
        pinned, pin_h = pins(H, lock, xs, zs, core) if lock.any() else (np.zeros(len(xs), bool), np.zeros(len(xs)))
        ps, km, bridged, k = [], 0.0, 0.0, 0
        for x, z in samples:
            p, b = profile(H, x, z, level, pinned[k:k + len(x)], pin_h[k:k + len(x)])
            ps.append(p)
            k += len(x)
            km += (len(x) - 1) * DS / 1000
            bridged += b
        ps = np.concatenate(ps).astype(np.float32)
        core = level["width"] / 2 + NODE_MARGIN
        touch, new_lock = stamp(H, lock, xs, zs, ps, core, core + BLEND)
        lo = before[touch] - (level["cut"] + SIDE_EXTRA)       # never move a grid point further than
        hi = before[touch] + (level["fill"] + SIDE_EXTRA)      # this, even on a cliff or a wrong OSM line
        H[touch] = np.clip(H[touch], lo, hi)
        changed = int(touch.sum())
        bed = new_lock & ~lock
        d = (H - before)[bed]
        lock |= new_lock
        st = dict(name=level["name"], roads=len(chains), km=km, points=changed, bridged=bridged,
                  mean=float(np.abs(d).mean()) if d.size else 0.0,
                  fill=float(d.max()) if d.size else 0.0, cut=float(d.min()) if d.size else 0.0)
        stats.append(st)
        if not quiet:
            log(f"  {st['name']:15s} {st['roads']:6d} roads {st['km']:7.1f} km   bed points {int(bed.sum()):8d}   "
                f"average change {st['mean']:.2f} m, most fill +{st['fill']:.1f} m, most cut {st['cut']:.1f} m, "
                f"over water {st['bridged']:.0f} m")
    return stats, lock


def main():
    base = r"D:\NapaMap\gis"
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dem", default=os.path.join(base, "full", "full_dem_water.tif"))
    ap.add_argument("--guide", default=os.path.join(base, "full", "roads_guide", "napa_roads_guide"))
    ap.add_argument("--outdir", default=os.path.join(base, "full"))
    args = ap.parse_args()

    from osgeo import gdal
    gdal.UseExceptions()
    src = gdal.Open(args.dem)
    H = src.GetRasterBand(1).ReadAsArray().astype(np.float32)
    n = H.shape[0]
    log(f"Height map {n} x {n}, {H.min():.2f} to {H.max():.2f} m")
    recs = R.read_shapefile(args.guide)
    log(f"{len(recs)} guide lines")

    before = H.copy()
    stats, lock = build(H, recs)
    diff = H - before
    log(f"Road bed covers {lock.sum() * CELL * CELL / 1e6:.1f} km2; ground changed by more than 10 cm on "
        f"{(np.abs(diff) > 0.1).sum() * CELL * CELL / 1e6:.1f} km2")
    for sign, name in ((1, "fill"), (-1, "cut")):  # the biggest changes, to look at in Buldozer
        order = np.argsort((sign * diff).ravel())[::-1][:2000]
        seen = []
        for k in order:
            r, c = divmod(int(k), n)
            x, z = c * CELL, (n - 1 - r) * CELL
            if all(math.hypot(x - a, z - b) > 150 for a, b, _ in seen):
                seen.append((x, z, float(diff[r, c])))
            if len(seen) == 5:
                break
        log(f"Biggest {name}: " + ", ".join(f"{v:+.1f} m at {x:.0f} / {z:.0f}" for x, z, v in seen))

    os.makedirs(args.outdir, exist_ok=True)
    tif = os.path.join(args.outdir, "full_dem_roads.tif")
    out = gdal.GetDriverByName("GTiff").Create(tif, n, n, 1, gdal.GDT_Float32, ["COMPRESS=DEFLATE"])
    out.SetGeoTransform(src.GetGeoTransform())
    out.SetProjection(src.GetProjection())
    out.GetRasterBand(1).WriteArray(H)
    out = None
    asc = os.path.join(args.outdir, "napa_dem_roads.asc")
    size = n * CELL
    gdal.Translate(asc, tif, format="AAIGrid", outputSRS="EPSG:32631",
                   outputBounds=[ORIGIN_E, size, ORIGIN_E + size, 0])
    log(f"Wrote {tif}")
    log(f"Wrote {asc} (+ .prj)")


if __name__ == "__main__":
    sys.exit(main())
