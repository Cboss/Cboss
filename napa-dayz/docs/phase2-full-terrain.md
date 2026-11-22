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

### Checked before processing

Both mosaics were test-built at low resolution straight from the USGS and Planetary Computer servers:

- **Heights:** all 46 files join (all five surveys are NAD83 / UTM 10N; each keeps its own no-data value, so the newer partial surveys sit on top and the older ones fill the gaps). 100% coverage, real heights −1.3 to 813 m, so **in-game −1.1 to 723 m** after the 8/9 scale
- **Photos:** all 24 tiles join with no holes. The town on the far west edge, halfway up, is the east side of Sonoma

## 2. Process

Run `gis/full_process.bat` from the OSGeo4W Shell. It writes into `D:\NapaMap\gis\full\`:

| File | For |
|---|---|
| `napa_dem.asc` + `napa_dem.prj` | Terrain Builder height import (4096 grid, 5 m, UTM 31N label) |
| `napa_dem_wm16.png` | World Machine (16-bit, −10 to 1000 m) |
| `napa_sat.png` | Satellite image, 20,480 px |
| `napa_nir.png` | Near-infrared, for the surface mask |
| `preview_sat_2048.png` | Quick look for gaps / black holes |

Check the printed height min/max: expect about **−3.8 and 725.5** (after the −1.5 m water-level drop). A huge negative minimum (−999999 or −3.4e+38) means a missing height tile.

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

## Water level: decided, lower 1.5 m

DayZ's sea is at 0 m. Lidar records the river's water surface, not its bed: the Napa River downtown and at the Oxbow is 0.74 m real, 0.66 m after scaling, so without an offset it would be a dry channel.

**Decision (Boss): lower all heights by 1.5 m.** In-game height = real × 0.8889 − 1.5.

| Spot | In-game after −1.5 m |
|---|---|
| Napa River, downtown / Oxbow | about −0.8 m: water, knee-to-waist deep |
| River by the airport | about −0.5 m: water |
| Napa-Sonoma marsh | about −1.3 to −0.7 m: tidal water, the south becomes coastline and sloughs |
| Downtown streets by the river | about 3.5 m: dry |
| Carneros vineyards | about 30 m |

Phase 4 can carve the river channel deeper in Terrain Builder so it is swimmable.

To apply: `full_process.bat dem` (height map only; the satellite image is unchanged).

## 5. Buldozer check: passed

Generate layers produced 13,918 files (2 GB) in `P:\Napa\data` with no errors. In Buldozer the bay marsh and sloughs south of the airport are flooded (the −1.5 m drop works) and the eastern hills near Skyline Park show full relief.

The hard line where the photo switches to the close-up grass texture is a Buldozer thing; in game the two blend over distance (`noDetailDist` / `fullDetailDist` in `config.cpp`).

## 6. Into the game (Workshop + Architect test server)

Files: [`terrain/napa/`](../terrain/napa/). Same steps as the test patch ([`testing-in-game.md`](testing-in-game.md)), with these names:

| Item | Test patch | Full map |
|---|---|---|
| World class / mission suffix | `NapaPilot` | `Napa` |
| WRP export | `P:\NapaPilot\world\NapaPilot.wrp` | `P:\Napa\world\Napa.wrp` |
| `config.cpp` | `P:\NapaPilot\config.cpp` | `P:\Napa\config.cpp` (from `terrain/napa/config.cpp`) |
| CE folder | `P:\NapaPilot\ce\` | `P:\Napa\ce\` (from `terrain/napa/ce/`) |
| Addon Builder source / prefix | `P:\NapaPilot` / `NapaPilot` | `P:\Napa` / `Napa` |
| Mod folder | `@NapaPilot` | `@Napa` |
| Mission | `dayzOffline.NapaPilot` | `dayzOffline.Napa` (copy of Chernarus + the 4 files in `terrain/napa/mission/dayzOffline.Napa/`) |

The full-map `config.cpp` adds 2D-map labels (Napa, Oxbow, Yountville, Veterans Home, Carneros, Napa State Hospital, Skyline Park, Napa County Airport) and 10 fresh-spawn areas on dry land across the valley (Carneros, Napa west side, Browns Valley, Coombsville, Imola, Oak Knoll, Silverado Trail, the north valley floor, Yountville).

### Keep the PBO small

Addon Builder's "files to copy directly" list includes `*.png`, so every PNG in `P:\Napa` (a PNG copy of each texture tile in `data\layers`) would be packed. The default exclusion list already skips `*\Source\*`, so `P:\Napa\source` is safe.

Use [`terrain/napa/napa_exclude.lst`](../terrain/napa/napa_exclude.lst): the DayZ Tools default `exclude.lst` plus `*.png`, `*.asc`, `*.prj`, `*.tif`, `*.vrt`, `*.aux.xml`, `*.tv4p`, `*.v4d`. Save it as `D:\NapaMap\napa_exclude.lst`, then Addon Builder → Options → **Exclusion pattern list filename**: untick **Use default** and pick it. Switch back to **Use default** before packing other mods.
