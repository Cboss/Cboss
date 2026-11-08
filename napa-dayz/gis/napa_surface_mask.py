"""
Napa DayZ map: build the surface mask (Phase 3).

Run from the OSGeo4W Shell (its Python has GDAL and numpy):
    python napa_surface_mask.py

Combines three sources into one colour per pixel for Terrain Builder:
  * the 2022 NAIP photo (red, green, blue, near-infrared) -> vegetation vs. bare vs. pavement
  * OpenStreetMap roads, land use and water               -> exact roads, vineyards, runways, water
  * the processed height map                               -> anything under DayZ sea level

Four surfaces only, so no Terrain Builder tile can exceed the 4-materials-per-tile limit:

  surface        colour (R,G,B)   material (copy of vanilla)            used for
  napa_grass     (  0, 255,   0)  cp_grass.rvmat                        open grassland, the golden hills
  napa_forest    (  0, 110,   0)  cp_broadleaf_sparse1.rvmat            oak woodland, forest
  napa_dirt      (150, 100,  50)  cp_dirt.rvmat                         vineyards, bare ground, tracks, riverbeds, ponds, marsh mud
  napa_concrete  (128, 128, 128)  cp_concrete1.rvmat                    paved roads, parking, runways, buildings, town
"""

import argparse
import os
import sys
import time

import numpy as np
from osgeo import gdal, ogr, osr

gdal.UseExceptions()
ogr.UseExceptions()

# ---------------------------------------------------------------- settings

# Real-world map area (EPSG:26910, NAD83 / UTM 10N). Same as full_process.bat.
XMIN, YMIN, XMAX, YMAX = 547000.0, 4228000.0, 570040.0, 4251040.0

GRASS, FOREST, DIRT, CONCRETE = 0, 1, 2, 3
NAMES = {GRASS: "napa_grass", FOREST: "napa_forest", DIRT: "napa_dirt", CONCRETE: "napa_concrete"}
COLOURS = {
    GRASS: (0, 255, 0),
    FOREST: (0, 110, 0),
    DIRT: (150, 100, 50),
    CONCRETE: (128, 128, 128),
}

# Photo thresholds (NAIP 2022, flown mid/late May; tuned on the Napa tiles)
NDVI_FOREST = 0.22      # tree canopy: green and ...
BRIGHT_FOREST = 95      # ... dark (mean of R,G,B)
NDVI_BARE = 0.02        # below this the ground is bare, built or dead
BRIGHT_BARE = 150       # bare soil / gravel is bright ...
BROWN_BARE = -8         # ... and brown: blue at least 8 below red
NDVI_PAVED = -0.04      # pavement and roofs reflect less near-infrared than red (dry grass doesn't) ...
BLUE_PAVED = -4         # ... and are grey-blue: blue no more than 4 below red (dry grass is yellow)
DARK_PAVED = 60         # ... and not in deep shadow
NDVI_WATER = -0.15      # open water: strongly negative NDVI ...
NIR_WATER = 70          # ... and almost no near-infrared (ponds ~40, pavement ~120)

# Road half-widths in metres (real world) by OSM highway class
PAVED_ROADS = {
    "motorway": 9, "trunk": 8, "primary": 7, "secondary": 6, "tertiary": 5,
    "motorway_link": 4, "trunk_link": 4, "primary_link": 4, "secondary_link": 4, "tertiary_link": 4,
    "unclassified": 4, "residential": 4, "living_street": 3.5, "service": 3,
}
DIRT_ROADS = {"track": 2}


# ---------------------------------------------------------------- helpers

def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def utm():
    s = osr.SpatialReference()
    s.ImportFromEPSG(26910)
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return s


def wgs84():
    s = osr.SpatialReference()
    s.ImportFromEPSG(4326)
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return s


def blank(size):
    """In-memory byte raster covering the map area at size x size."""
    ds = gdal.GetDriverByName("MEM").Create("", size, size, 1, gdal.GDT_Byte)
    px = (XMAX - XMIN) / size
    ds.SetGeoTransform((XMIN, px, 0, YMAX, 0, -px))
    ds.SetProjection(utm().ExportToWkt())
    return ds


def osm_features(path, layer_name, where):
    """Yield (feature, geometry in UTM metres) from an .osm file layer."""
    if not os.path.exists(path):
        log(f"  (skipped: {path} not found)")
        return
    gdal.SetConfigOption("OSM_USE_CUSTOM_INDEXING", "NO")
    src = ogr.Open(path)
    lyr = src.GetLayerByName(layer_name)
    lyr.SetAttributeFilter(where)
    ct = osr.CoordinateTransformation(wgs84(), utm())
    for f in lyr:
        g = f.GetGeometryRef()
        if g is None:
            continue
        g = g.Clone()
        g.Transform(ct)
        yield f, g


def rasterize(size, items):
    """Burn a list of UTM geometries into a 0/1 array of size x size.
    ALL_TOUCHED only on coarse test runs (pixels over 2 m), so roads keep their true width at 1 m."""
    ds = blank(size)
    mem = ogr.GetDriverByName("Memory").CreateDataSource("")
    lyr = mem.CreateLayer("x", utm(), ogr.wkbUnknown)
    defn = lyr.GetLayerDefn()
    n = 0
    for g in items:
        f = ogr.Feature(defn)
        f.SetGeometry(g)
        lyr.CreateFeature(f)
        n += 1
    if n:
        touched = "TRUE" if (XMAX - XMIN) / size > 2 else "FALSE"
        gdal.RasterizeLayer(ds, [1], lyr, burn_values=[1], options=[f"ALL_TOUCHED={touched}"])
    return ds.GetRasterBand(1).ReadAsArray().astype(bool), n


def box_count(a, r):
    """For each pixel, how many True pixels in the (2r+1)x(2r+1) box around it."""
    p = np.pad(a.astype(np.int32), r, mode="edge")
    c = np.zeros((p.shape[0] + 1, p.shape[1] + 1), np.int32)   # integral image with a zero row/column
    c[1:, 1:] = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    n, m = a.shape
    return c[k:k + n, k:k + m] - c[:n, k:k + m] - c[k:k + n, :m] + c[:n, :m]


def majority(cls, r, classes):
    """Majority filter: each pixel takes the most common class in its box (removes speckle)."""
    counts = np.stack([box_count(cls == c, r) for c in classes])
    return np.asarray(classes, dtype=np.uint8)[counts.argmax(0)]


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = r"D:\NapaMap\gis"
    ap.add_argument("--naip", default=os.path.join(base, "full", "full_naip.tif"))
    ap.add_argument("--dem", default=os.path.join(base, "full", "full_dem_s.tif"),
                    help="in-game heights (after x0.8889 - 1.5)")
    ap.add_argument("--osm", default=os.path.join(base, "raw", "osm"),
                    help="folder with roads.osm, landuse.osm, water.osm, buildings.osm")
    ap.add_argument("--out", default=os.path.join(base, "full", "napa_mask.png"))
    ap.add_argument("--size", type=int, default=20480, help="output size in pixels (20480 = 1 m)")
    ap.add_argument("--strip", type=int, default=1024, help="rows per processing strip")
    args = ap.parse_args()

    size = args.size
    px = (XMAX - XMIN) / size            # real metres per output pixel
    log(f"Napa surface mask: {size} x {size} px, {px:.3f} m real per pixel")

    # ---------------- OpenStreetMap layers
    o = lambda name: os.path.join(args.osm, name)

    log("OSM: paved roads")
    geoms = []
    for f, g in osm_features(o("roads.osm"), "lines", "highway IS NOT NULL"):
        w = PAVED_ROADS.get(f.GetField("highway"))
        other = f.GetField("other_tags") or ""
        if w and '"surface"=>"unpaved"' not in other and '"surface"=>"gravel"' not in other \
                and '"surface"=>"dirt"' not in other:
            geoms.append(g.Buffer(w))
    paved, n = rasterize(size, geoms)
    log(f"  {n} roads")

    log("OSM: tracks and unpaved roads")
    geoms = []
    for f, g in osm_features(o("roads.osm"), "lines", "highway IS NOT NULL"):
        hw = f.GetField("highway")
        other = f.GetField("other_tags") or ""
        unpaved = any(f'"surface"=>"{s}"' in other for s in ("unpaved", "gravel", "dirt", "ground", "compacted"))
        if hw in DIRT_ROADS or (hw in PAVED_ROADS and unpaved):
            geoms.append(g.Buffer(DIRT_ROADS.get(hw, 3)))
    tracks, n = rasterize(size, geoms)
    log(f"  {n} tracks")

    log("OSM: runways, taxiways, aprons, parking")
    geoms = []
    # Runways and taxiways are mapped as lines; "aeroway" sits in other_tags on the lines layer
    for f, g in osm_features(o("landuse.osm"), "lines", "other_tags LIKE '%\"aeroway\"=>\"runway\"%'"):
        geoms.append(g.Buffer(23))          # Napa County Airport main runway is 150 ft wide
    for f, g in osm_features(o("landuse.osm"), "lines", "other_tags LIKE '%\"aeroway\"=>\"taxiway\"%'"):
        geoms.append(g.Buffer(11))
    for f, g in osm_features(o("landuse.osm"), "multipolygons",
                             "aeroway IN ('runway','taxiway','apron') OR amenity = 'parking'"):
        geoms.append(g)
    hard, n = rasterize(size, geoms)
    log(f"  {n} areas")

    log("OSM: buildings")
    geoms = [g for f, g in osm_features(o("buildings.osm"), "multipolygons", "building IS NOT NULL")]
    buildings, n = rasterize(size, geoms)
    log(f"  {n} buildings")

    log("OSM: vineyards")
    geoms = [g for f, g in osm_features(o("landuse.osm"), "multipolygons", "landuse = 'vineyard'")]
    vineyard, n = rasterize(size, geoms)
    log(f"  {n} vineyards")

    log("OSM: water")
    geoms = [g for f, g in osm_features(o("water.osm"), "multipolygons", "natural = 'water'")]
    for f, g in osm_features(o("water.osm"), "lines", "waterway IN ('river','canal')"):
        geoms.append(g.Buffer(6))
    water, n = rasterize(size, geoms)
    log(f"  {n} water features")

    # ---------------- height map: anything under DayZ sea level
    log("Height map")
    dem = gdal.Warp("", args.dem, format="MEM", width=size, height=size,
                    outputBounds=(XMIN, YMIN, XMAX, YMAX), resampleAlg="bilinear")
    under = dem.GetRasterBand(1).ReadAsArray() < 0.0
    dem = None

    # ---------------- photo, strip by strip
    naip = gdal.Open(args.naip)
    if (naip.RasterXSize, naip.RasterYSize) != (20480, 20480):
        log(f"  note: photo is {naip.RasterXSize} px, resampling to {size}")
    scale = naip.RasterYSize / size

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    out_tif = os.path.splitext(args.out)[0] + "_tmp.tif"
    drv = gdal.GetDriverByName("GTiff")
    out = drv.Create(out_tif, size, size, 3, gdal.GDT_Byte, ["COMPRESS=DEFLATE", "TILED=YES", "BIGTIFF=IF_SAFER"])
    out.SetGeoTransform((XMIN, px, 0, YMAX, 0, -px))
    out.SetProjection(utm().ExportToWkt())

    lut = np.zeros((4, 3), np.uint8)
    for c, rgb in COLOURS.items():
        lut[c] = rgb
    totals = np.zeros(4, np.int64)

    R = 2                                   # majority filter radius (photo classes only)
    for y0 in range(0, size, args.strip):
        y1 = min(size, y0 + args.strip)
        a0, a1 = max(0, y0 - R), min(size, y1 + R)          # strip plus halo
        sy0, sy1 = int(round(a0 * scale)), int(round(a1 * scale))
        bands = naip.ReadRaster(0, sy0, naip.RasterXSize, sy1 - sy0,
                                buf_xsize=size, buf_ysize=a1 - a0, band_list=[1, 2, 3, 4])
        img = np.frombuffer(bands, np.uint8).reshape(4, a1 - a0, size).astype(np.float32)
        r, g, b, nir = img
        ndvi = (nir - r) / (nir + r + 1e-6)
        bright = (r + g + b) / 3.0
        blue_minus_red = b - r

        cls = np.full(r.shape, GRASS, np.uint8)
        cls[(ndvi >= NDVI_FOREST) & (bright < BRIGHT_FOREST)] = FOREST
        cls[(ndvi < NDVI_BARE) & (bright >= BRIGHT_BARE) & (blue_minus_red < BROWN_BARE)] = DIRT
        cls[(ndvi < NDVI_PAVED) & (blue_minus_red > BLUE_PAVED) & (bright > DARK_PAVED)] = CONCRETE
        cls[(ndvi < NDVI_WATER) & (nir < NIR_WATER)] = DIRT      # ponds and reservoirs: muddy bottom
        cls = majority(cls, R, [GRASS, FOREST, DIRT, CONCRETE])[y0 - a0:(y0 - a0) + (y1 - y0)]

        s = slice(y0, y1)
        cls[vineyard[s] & (cls != FOREST)] = DIRT
        cls[under[s] | water[s]] = DIRT
        cls[tracks[s]] = DIRT
        cls[paved[s] | hard[s] | buildings[s]] = CONCRETE

        totals += np.bincount(cls.ravel(), minlength=4)
        rgb = lut[cls]
        for i in range(3):
            out.GetRasterBand(i + 1).WriteArray(np.ascontiguousarray(rgb[..., i]), 0, y0)
        log(f"  rows {y0}-{y1} done")

    out.FlushCache()
    out = None
    naip = None

    log("Writing PNG")
    gdal.Translate(args.out, out_tif, format="PNG", creationOptions=["ZLEVEL=6"])
    prev = os.path.splitext(args.out)[0] + "_preview.png"
    gdal.Translate(prev, out_tif, format="PNG", width=2048, height=2048, resampleAlg="nearest")
    os.remove(out_tif)
    for p in (args.out + ".aux.xml", prev + ".aux.xml"):
        if os.path.exists(p):
            os.remove(p)

    log("Done. Share of the map:")
    for c in (GRASS, FOREST, DIRT, CONCRETE):
        log(f"  {NAMES[c]:14s} {100 * totals[c] / totals.sum():5.1f}%")
    log(f"Mask:    {args.out}")
    log(f"Preview: {prev}")


if __name__ == "__main__":
    sys.exit(main())
