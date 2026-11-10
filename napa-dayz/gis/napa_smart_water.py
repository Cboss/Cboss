"""
Napa DayZ map: "smart water" heights (Phase 4).

Run from the OSGeo4W Shell:
    python napa_smart_water.py

The 1.5 m drop (Phase 2) put the Napa River below DayZ sea level, but it also flooded about
26 km2 of flat tidal marsh in the south. This keeps real water as water and turns the rest
into walkable wetland flats just above the waterline:

  * water  = OpenStreetMap water areas (river, sloughs, ponds) + river lines + open water in
             the photo (very low near-infrared), but only where the ground is near sea level
  * water cells are lowered to at least WATER_DEPTH below sea level (swimmable)
  * every other cell that was below LAND_MIN is lifted into LAND_MIN..LAND_TOP, keeping its
    small bumps and channels, so the marsh is dry, flat and walkable
  * a light blur along the shoreline softens the banks

Inland ponds and reservoirs higher up are left alone: DayZ's sea can't fill them, they get
pond objects later.

Writes (in D:\\NapaMap\\gis\\full\\):
  full_dem_water.tif    in-game heights, 4096 x 4096
  napa_dem_water.asc    + .prj, ready for Terrain Builder (same layout as napa_dem.asc)
  water_preview.png     photo with the final water in blue and the lifted marsh in yellow
"""

import argparse
import os
import sys
import time

import numpy as np
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
ogr.UseExceptions()

XMIN, YMIN, XMAX, YMAX = 547000.0, 4228000.0, 570040.0, 4251040.0

NEAR_SEA = 1.0       # only water at or below this in-game height counts as sea-connected
WATER_DEPTH = -2.0   # water cells are at least this deep (in-game metres)
LAND_MIN = 0.4       # dry land never lower than this
LAND_TOP = 0.9       # lifted marsh is squeezed into LAND_MIN..LAND_TOP
RIVER_HALF_WIDTH = 8 # buffer for OSM river/canal lines (real metres)
PHOTO_WATER_SHARE = 0.5  # a cell is open water if at least half its photo pixels are water


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def srs(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return s


def osm_water(path, n):
    """OSM water areas and river lines burned into an n x n boolean grid."""
    ds = gdal.GetDriverByName("MEM").Create("", n, n, 1, gdal.GDT_Byte)
    px = (XMAX - XMIN) / n
    ds.SetGeoTransform((XMIN, px, 0, YMAX, 0, -px))
    ds.SetProjection(srs(26910).ExportToWkt())
    if not os.path.exists(path):
        log(f"  {path} not found: using the photo only")
        return np.zeros((n, n), bool), 0

    vec = "MEM" if int(gdal.VersionInfo()) >= 3110000 else "Memory"
    mem = ogr.GetDriverByName(vec).CreateDataSource("")
    lyr = mem.CreateLayer("w", srs(26910), ogr.wkbUnknown)
    ct = osr.CoordinateTransformation(srs(4326), srs(26910))
    src = ogr.Open(path)
    count = 0
    for layer, where, buf in (("multipolygons", "natural = 'water'", 0),
                              ("lines", "waterway IN ('river','canal')", RIVER_HALF_WIDTH)):
        L = src.GetLayerByName(layer)
        L.SetAttributeFilter(where)
        for f in L:
            g = f.GetGeometryRef()
            if g is None:
                continue
            g = g.Clone()
            g.Transform(ct)
            if buf:
                g = g.Buffer(buf)
            o = ogr.Feature(lyr.GetLayerDefn())
            o.SetGeometry(g)
            lyr.CreateFeature(o)
            count += 1
    gdal.RasterizeLayer(ds, [1], lyr, burn_values=[1], options=["ALL_TOUCHED=TRUE"])
    return ds.GetRasterBand(1).ReadAsArray().astype(bool), count


def photo_water(path, n):
    """Share of open-water pixels (very low near-infrared) in each of the n x n cells."""
    if not os.path.exists(path):
        log(f"  {path} not found: using OSM only")
        return np.zeros((n, n), np.float32)
    naip = gdal.Open(path)
    share = np.zeros((n, n), np.float32)
    rows = naip.RasterYSize // n                      # photo rows per cell (5 at full size)
    step = 256                                        # cells per strip
    for c0 in range(0, n, step):
        c1 = min(n, c0 + step)
        r0, r1 = c0 * naip.RasterYSize // n, c1 * naip.RasterYSize // n
        red = naip.GetRasterBand(1).ReadAsArray(0, r0, naip.RasterXSize, r1 - r0).astype(np.float32)
        nir = naip.GetRasterBand(4).ReadAsArray(0, r0, naip.RasterXSize, r1 - r0).astype(np.float32)
        ndvi = (nir - red) / (nir + red + 1e-6)
        w = ((ndvi < -0.15) & (nir < 70)).astype(np.float32)
        k = naip.RasterXSize // n
        w = w[: (c1 - c0) * k, : n * k].reshape(c1 - c0, k, n, k).mean(axis=(1, 3))
        share[c0:c1] = w
    return share


def box_mean(a, r):
    p = np.pad(a, r, mode="edge").astype(np.float64)
    c = np.zeros((p.shape[0] + 1, p.shape[1] + 1))
    c[1:, 1:] = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    n, m = a.shape
    return (c[k:k + n, k:k + m] - c[:n, k:k + m] - c[k:k + n, :m] + c[:n, :m]) / (k * k)


def main():
    base = r"D:\NapaMap\gis"
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dem", default=os.path.join(base, "full", "full_dem_s.tif"))
    ap.add_argument("--naip", default=os.path.join(base, "full", "full_naip.tif"))
    ap.add_argument("--osm", default=os.path.join(base, "raw", "osm", "water.osm"))
    ap.add_argument("--outdir", default=os.path.join(base, "full"))
    args = ap.parse_args()

    dem = gdal.Open(args.dem)
    h = dem.GetRasterBand(1).ReadAsArray().astype(np.float64)
    n = h.shape[0]
    log(f"Height map {n} x {n}, in-game {h.min():.2f} to {h.max():.2f} m")

    log("OSM water")
    w_osm, count = osm_water(args.osm, n)
    log(f"  {count} water features")
    log("Photo water")
    w_photo = photo_water(args.naip, n) >= PHOTO_WATER_SHARE

    water = (w_osm | w_photo) & (h < NEAR_SEA)
    before = (h < 0).sum()

    out = h.copy()
    out[water] = np.minimum(h[water], WATER_DEPTH)
    low_land = (~water) & (h < LAND_TOP)
    lo = h.min()
    out[low_land] = LAND_MIN + (h[low_land] - lo) / (LAND_TOP - lo) * (LAND_TOP - LAND_MIN)

    # soften the banks: blur a 2-cell band either side of the shoreline, keep water wet
    edge = box_mean(water.astype(np.float64), 2)
    band = (edge > 0) & (edge < 1)
    soft = box_mean(out, 1)
    out[band] = soft[band]
    out[water] = np.minimum(out[water], -0.5)
    out[(~water) & (out < LAND_MIN)] = LAND_MIN

    cell_km2 = ((XMAX - XMIN) / n / 1000) ** 2
    log(f"Under water before: {before * cell_km2:5.1f} km2   after: {(out < 0).sum() * cell_km2:5.1f} km2")
    log(f"Marsh lifted to dry land: {(low_land & (h < 0)).sum() * cell_km2:5.1f} km2")

    os.makedirs(args.outdir, exist_ok=True)
    tif = os.path.join(args.outdir, "full_dem_water.tif")
    drv = gdal.GetDriverByName("GTiff")
    o = drv.Create(tif, n, n, 1, gdal.GDT_Float32, ["COMPRESS=DEFLATE"])
    o.SetGeoTransform(dem.GetGeoTransform())
    o.SetProjection(dem.GetProjection())
    o.GetRasterBand(1).WriteArray(out.astype(np.float32))
    o = None

    asc = os.path.join(args.outdir, "napa_dem_water.asc")
    cell = 5.0                                   # in-game metres per height cell
    size = n * cell
    gdal.Translate(asc, tif, format="AAIGrid", outputSRS="EPSG:32631",
                   outputBounds=[200000, size, 200000 + size, 0])
    log(f"Wrote {tif}")
    log(f"Wrote {asc} (+ .prj)")

    # preview: photo, water blue, lifted marsh yellow
    try:
        k = 2048
        ph = gdal.Open(args.naip).ReadAsArray(buf_xsize=k, buf_ysize=k, band_list=[1, 2, 3])
        rgb = np.transpose(ph, (1, 2, 0)).astype(np.float32)
        idx = (np.arange(k) * n // k)
        wv = water[np.ix_(idx, idx)]
        lv = (low_land & (h < 0))[np.ix_(idx, idx)]
        rgb[wv] = 0.35 * rgb[wv] + 0.65 * np.array([30, 90, 220])
        rgb[lv] = 0.5 * rgb[lv] + 0.5 * np.array([230, 200, 60])
        prev = gdal.GetDriverByName("MEM").Create("", k, k, 3, gdal.GDT_Byte)
        for i in range(3):
            prev.GetRasterBand(i + 1).WriteArray(rgb[..., i].clip(0, 255).astype(np.uint8))
        p = os.path.join(args.outdir, "water_preview.png")
        gdal.GetDriverByName("PNG").CreateCopy(p, prev)
        log(f"Wrote {p}")
    except Exception as e:                       # preview is optional
        log(f"(preview skipped: {e})")


if __name__ == "__main__":
    sys.exit(main())
