"""
Napa DayZ map: OpenStreetMap roads as a tracing guide for Terrain Builder (Phase 4c).

    python napa_roads_guide.py [--osm D:\\NapaMap\\gis\\raw\\osm\\roads.osm] [--out D:\\NapaMap\\gis\\full\\roads_guide]

Reads the OSM roads, converts them from real-world UTM to Terrain Builder map coordinates
(origin 200000 / 0, 8/9 scale, same as the height map) and writes a shapefile with one line
per road. Each road gets the DayZ road-part family to build it with:

  family  OSM highway                                  Napa examples
  asf1    motorway, trunk (+ links)                    Hwy 29, Hwy 12/121, Hwy 221
  asf2    primary, secondary (+ links)                 Silverado Trail, Trancas, Imola, Soscol
  asf3    tertiary, unclassified (+ links)             other two-lane roads
  city    residential, living_street, service          town streets, driveways, lots
  grav    track                                        vineyard and farm tracks

Footpaths, cycleways and steps are left out.
"""

import argparse
import os
import sys

from osgeo import gdal, ogr, osr

gdal.UseExceptions()
ogr.UseExceptions()

XMIN, YMIN, XMAX, YMAX = 547000.0, 4228000.0, 570040.0, 4251040.0   # real-world UTM 10N
SCALE = 20480.0 / 23040.0                                           # 8/9
ORIGIN_E = 200000.0                                                 # Terrain Builder easting

FAMILY = {
    "motorway": "asf1", "motorway_link": "asf1", "trunk": "asf1", "trunk_link": "asf1",
    "primary": "asf2", "primary_link": "asf2", "secondary": "asf2", "secondary_link": "asf2",
    "tertiary": "asf3", "tertiary_link": "asf3", "unclassified": "asf3",
    "residential": "city", "living_street": "city", "service": "city",
    "track": "grav",
}


def srs(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    return s


def tag(other, key):
    """Value of key in OGR's other_tags string ('"k"=>"v","k2"=>"v2"')."""
    if not other:
        return ""
    needle = f'"{key}"=>"'
    i = other.find(needle)
    if i < 0:
        return ""
    j = other.find('"', i + len(needle))
    return other[i + len(needle):j]


def main():
    base = r"D:\NapaMap\gis"
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--osm", default=os.path.join(base, "raw", "osm", "roads.osm"))
    ap.add_argument("--out", default=os.path.join(base, "full", "roads_guide"))
    args = ap.parse_args()

    to_utm = osr.CoordinateTransformation(srs(4326), srs(26910))
    clip = ogr.CreateGeometryFromWkt(f"POLYGON(({XMIN} {YMIN},{XMAX} {YMIN},{XMAX} {YMAX},{XMIN} {YMAX},{XMIN} {YMIN}))")

    os.makedirs(args.out, exist_ok=True)
    shp = os.path.join(args.out, "napa_roads_guide.shp")
    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(shp):
        drv.DeleteDataSource(shp)
    ds = drv.CreateDataSource(shp)
    lyr = ds.CreateLayer("napa_roads_guide", srs(32631), ogr.wkbLineString, ["ENCODING=UTF-8"])
    for name, width in (("osm_id", 16), ("highway", 16), ("family", 6), ("name", 60), ("ref", 20)):
        f = ogr.FieldDefn(name, ogr.OFTString)
        f.SetWidth(width)
        lyr.CreateField(f)
    f = ogr.FieldDefn("length_m", ogr.OFTReal)
    lyr.CreateField(f)

    src = ogr.Open(args.osm)
    lines = src.GetLayerByName("lines")
    lines.SetAttributeFilter("highway IS NOT NULL")
    counts, lengths = {}, {}
    for feat in lines:
        hw = feat.GetField("highway")
        fam = FAMILY.get(hw)
        if not fam:
            continue
        g = feat.GetGeometryRef()
        if g is None:
            continue
        g = g.Clone()
        g.Transform(to_utm)
        g = g.Intersection(clip)
        if g is None or g.IsEmpty():
            continue
        parts = [g.GetGeometryRef(i) for i in range(g.GetGeometryCount())] \
            if g.GetGeometryType() in (ogr.wkbMultiLineString, ogr.wkbMultiLineString25D) else [g]
        for part in parts:
            if part.GetGeometryType() not in (ogr.wkbLineString, ogr.wkbLineString25D):
                continue
            out = ogr.Geometry(ogr.wkbLineString)
            for i in range(part.GetPointCount()):
                x, y = part.GetX(i), part.GetY(i)
                out.AddPoint_2D(ORIGIN_E + (x - XMIN) * SCALE, (y - YMIN) * SCALE)
            o = ogr.Feature(lyr.GetLayerDefn())
            o.SetGeometry(out)
            o.SetField("osm_id", str(feat.GetField("osm_id") or ""))
            o.SetField("highway", hw)
            o.SetField("family", fam)
            o.SetField("name", (feat.GetField("name") or "")[:60])
            o.SetField("ref", tag(feat.GetField("other_tags"), "ref")[:20])
            o.SetField("length_m", round(out.Length(), 1))
            lyr.CreateFeature(o)
            counts[fam] = counts.get(fam, 0) + 1
            lengths[fam] = lengths.get(fam, 0.0) + out.Length()
    ds = None

    print(f"Wrote {shp}")
    for fam in ("asf1", "asf2", "asf3", "city", "grav"):
        print(f"  {fam:5s} {counts.get(fam, 0):6d} lines  {lengths.get(fam, 0) / 1000:7.1f} km (in-game)")


if __name__ == "__main__":
    sys.exit(main())
