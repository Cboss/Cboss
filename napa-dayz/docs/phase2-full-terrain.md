# Phase 2: full terrain

Same steps as the test patch, at 20.48 km. Settings are in [`map-spec.md`](map-spec.md).

## 1. Downloads

Free space needed: about 40–60 GB (D: has 306 GB).

Search box (the map area plus a ~500 m margin), used to pick the tiles:

| Edge | Decimal degrees |
|---|---|
| North (Y max) | `38.416` |
| South (Y min) | `38.190` |
| East (X max) | `-122.190` |
| West (X min) | `-122.470` |

### USGS height data → `D:\NapaMap\gis\raw\full_dem\`

Run **`gis/download_full_dem.bat`** (no need for the website). It downloads 46 GeoTIFFs, about 11 GB, with curl, and writes `dem_list.txt`.

Why 46 files for 16 tiles: the area is covered by five lidar surveys (2017 Sacramento, 2018 NoCal Wildfires, 2022 Northern CA, 2023 Solano County, 2023 North Coast Ranges). The newer surveys only cover parts of each 10 km tile, so all of them are layered: `dem_list.txt` lists them oldest first, newest last, and `full_process.bat` builds the mosaic from it so the newest data sits on top and older surveys fill the gaps.

The list came from the USGS TNMAccess API (1-meter DEM, box above). The website's 1/3 arc-second results are 10 m data: don't use those.

### NAIP 2022 photos → `D:\NapaMap\gis\raw\full_naip\`

Run **`gis/download_full_naip.bat`**. It downloads 24 GeoTIFFs (4-band, 60 cm), about 10 GB, with curl.

- Source: Microsoft Planetary Computer's open-data copy of USDA NAIP (public domain). Its newest year for Napa is **2022** (flown 18–24 May 2022); 2024 is only on EarthExplorer. 2022 was chosen for the one-click download
- Coverage checked: the 24 tiles cover the whole map area with no gaps
- The test patch used 2024 imagery; the full map uses 2022 throughout, so colours match across the map

## 2. Process

Run `gis/full_process.bat` from the OSGeo4W Shell. It writes into `D:\NapaMap\gis\full\`:

| File | For |
|---|---|
| `napa_dem.asc` + `napa_dem.prj` | Terrain Builder height import (4096 grid, 5 m, UTM 31N label) |
| `napa_dem_wm16.png` | World Machine (16-bit, −10 to 1000 m) |
| `napa_sat.png` | Satellite image, 20,480 px |
| `napa_nir.png` | Near-infrared, for the surface mask |
| `preview_sat_2048.png` | Quick look for gaps / black holes |

Check the printed height min/max: a minimum around 0–5 m (bay marsh) and a maximum of several hundred metres (Mt. Veeder slopes, eastern hills) is right. A minimum of −999999 means a missing height tile.

## 3. World Machine (next)

Blend the map edges down into the sea, and generate erosion / flow maps for surface painting. Steps to come once the outputs above check out.

## 4. Terrain Builder

New project `P:\Napa\source\Napa.tv4p`, following [`terrain-builder-notes.md`](terrain-builder-notes.md):

| Setting | Value |
|---|---|
| Mapframe name | `Napa` |
| Output root | `P:\Napa\data\` |
| Easting / Northing | `200000` / `0` |
| Grid / cell size | `4096 × 4096` / `5` (20,480 m) |
| Satellite / mask image | `20480 × 20480` (1 m/px) |
| Tile size / overlap | `512` / `64` |

The "not evenly divisible by tile size" warning will appear again. With 5 m cells there is no tile setting that divides 4096 cells evenly without huge overlap, so the last row and column of tiles stick out past the edge. Harmless; Chernarus-style even division would need 7.5 m cells, which is too coarse for Napa.

## Water level (decide before Terrain Builder)

DayZ's sea is at 0 m. The Napa River and the sloughs near the airport sit around 0–2 m in the USGS data, so at 0 they come out as dry channels, and the bay marsh is barely above water. Options, to settle after looking at the processed heights:

- Leave as is (dry river bed, marsh just above the sea)
- Lower everything by a metre or two so the river and sloughs fill with sea water (the low marsh floods too)
