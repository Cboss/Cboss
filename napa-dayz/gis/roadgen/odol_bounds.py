"""
Bounding box of a binarized DayZ model (ODOL v56 .p3d), read from the file header.

    python odol_bounds.py model.p3d [more.p3d ...]

Prints, in the model's own coordinates (metres): bounding-box min and max, and the bounding
centre, which is the point Terrain Builder and the game use as the object's position.
Header layout after the LOD resolutions: flags, 2 sphere radii, 3 flags, aiming centre (3),
2 colours, view density, bbox min/max (relative to the bounding centre), visual bbox min/max,
bounding centre, geometry centre, centre of mass.
"""
import struct
import sys


def bounds(path):
    with open(path, "rb") as f:
        b = f.read(400)
    if b[:4] != b"ODOL":
        raise ValueError(f"{path}: not an ODOL model")
    ver, n = struct.unpack_from("<II", b, 4)
    f = struct.unpack_from("<32f", b, 12 + 4 * n + 4)
    half_min, half_max, centre = f[11:14], f[14:17], f[23:26]
    lo = tuple(c + h for c, h in zip(centre, half_min))
    hi = tuple(c + h for c, h in zip(centre, half_max))
    return dict(version=ver, lods=n, min=lo, max=hi, centre=centre)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = bounds(p)
        size = [h - l for l, h in zip(r["min"], r["max"])]
        print(f"{p}: ODOL v{r['version']}, size X {size[0]:.2f} Y {size[1]:.2f} Z {size[2]:.2f} m, "
              f"min {tuple(round(v, 2) for v in r['min'])}, max {tuple(round(v, 2) for v in r['max'])}, "
              f"centre {tuple(round(v, 2) for v in r['centre'])}")
