# Phase 4: water and roads

## 4a. Smart water (ready)

The Phase 2 drop of 1.5 m filled the Napa River but also flooded ~26 km² of flat tidal marsh. `gis/napa_smart_water.py` fixes the heights:

- **Water** = OSM water areas (`natural=water`: the river, sloughs, ponds) + OSM river/canal lines (8 m half-width) + open water in the photo (NDVI < −0.15 and near-infrared < 70 in at least half the cell), only where the ground is at or below 1 m in-game
- Water cells go to at least **−2 m** (swimmable)
- Every other cell below 0.9 m is lifted into **0.4–0.9 m**, keeping its small bumps and channels: dry, walkable marsh flats
- 2-cell blur along the shoreline for softer banks

Test at 22.5 m resolution: under water 32.6 km² → **11.2 km²**; 24.8 km² of marsh lifted to dry land. The Napa River runs continuously from downtown to the bay; Sonoma Creek and the sloughs stay water.

Higher inland ponds and vineyard reservoirs are not touched: DayZ's sea can't fill them. They get pond objects (4d).

**Steps:** OSGeo4W Shell →
```bat
curl -L -o D:\NapaMap\gis\phase4_smart_water.bat https://raw.githubusercontent.com/Cboss/Cboss/ccr-3b451e26-3japm5/napa-dayz/gis/phase4_smart_water.bat
D:\NapaMap\gis\phase4_smart_water.bat
```
Then Terrain Builder: Layers manager → right-click `napa_dem.asc` → **Refresh content from source** → mapframe Properties → Processing → **Rebuild terrain** → **File → Export → WRP** → Save. No need to regenerate layers. Repack, Workshop, restart.

## 4b. Object libraries

Bohemia's DayZ terrain sample ([DayZ-Samples/Test_Terrain](https://github.com/BohemiaInteractive/DayZ-Samples), ADPL-SA) ships Terrain Builder template libraries for the base-game objects: `roads.tml` (190 road parts), `water.tml` (244 ponds/streams), `plantsnew.tml` (193), `residential.tml` (187), `industrial.tml` (242), `military.tml`, `specific.tml`, `walls.tml`, `signs.tml`, `rocks.tml`, `ruins.tml`, `wrecks.tml`, `rail.tml`. Import them into Terrain Builder's Library manager instead of building the libraries by hand.

## 4c. Roads

DayZ roads are not painted from shapefiles like Arma 3: they are **prefab road parts** placed with Terrain Builder's **Road Tool** (Bohemia wiki: *DayZ: Using Road Tool in Terrain Builder*).

Road part families in `roads.tml`:

| Family | Use for in Napa |
|---|---|
| `asf1` | Hwy 29, Hwy 12/121, Hwy 221 (widest) |
| `asf2` | Silverado Trail, Trancas, Imola, Soscol, Jefferson |
| `asf3` | Other two-lane roads |
| `city` | Town streets |
| `grav` / `mud` | Tracks, vineyard roads |
| `kr_t_*` / `kr_x_*` | T and X junctions |
| `runway_*` | Napa County Airport |

Each family has straights (`_6`, `_12`, `_25`), ends (`_6konec`) and curves named angle + radius (`_10 25` = 10° on a 25 m radius … `_0 2000`).

### Road guide (ready)

`gis/napa_roads_guide.py` turns the OSM roads into a shapefile already in Terrain Builder map coordinates (200000 / 0, 8/9 scale, labelled UTM 31N like the height map), one line per road with its suggested road-part family. The result is in [`terrain/napa/roads_guide/`](../terrain/napa/roads_guide/):

| family | lines | in-game km | Includes |
|---|---|---|---|
| asf1 | 172 | 68 | CA 29 Saint Helena Hwy (27 km both directions), CA 12 Jameson Canyon |
| asf2 | 683 | 121 | CA 121 Monticello Rd, Silverado Trail, CA 221 Napa-Vallejo Hwy, Jefferson St, Carneros Hwy, Soscol Ave, Old Sonoma Rd |
| asf3 | 475 | 200 | Other two-lane roads |
| city | 11,388 | 1,654 | Residential streets, service roads, driveways, lots |
| grav | 316 | 140 | Vineyard and farm tracks |

Fields: `osm_id`, `highway`, `family`, `name`, `ref`, `length_m`. Divided highways (CA 29) have one line per direction.

Load it: download the 5 files into `P:\Napa\source\roads_guide\`, then Terrain Builder **File → Import → Shapes** → `napa_roads_guide.shp`. It sits on the map as a Shapes layer to trace with the Road Tool.

### Plan B: road parts generated from the guide (in progress)

The Road Tool refused to add roads ("Area tool - Couldn't use 'add Area' the target layer is locked", although no layer was locked). In the game roads are just objects, so `gis/napa_road_objects.py` lays the parts itself and writes a Terrain Builder object list for **File → Import → Objects**:

- Part geometry: `gis/roadgen/road_parts_asf1.csv`, measured from Bohemia's p3d files with `gis/roadgen/mlod.py` (memory points `LB`/`PB` begin, `LE`/`PE` end). Origin = begin centre, road along +Z, curves turn right; a curve laid backwards turns left. `asf1_12` is really 12.5 m long, `asf1_25` 25 m, `asf1_6` 6.25 m
- Joins OSM lines into whole roads: at each node the ends are paired straightest-first (within 30°), so a highway runs through the points where ramps leave it. All asf1 becomes 4 long roads
- Chooses parts with a beam search (looks ahead, keeps the 10 best partial roads per 5 m): parts sit a median 0.06 m off the OSM line, 99% within 1.1 m. The first version picked one part at a time and wobbled left-right on gentle curves (the part set has nothing between a 1000 m and a 100 m radius)
- Each road runs to its very end (may overshoot up to 7 m) so there are no wedge-shaped gaps where one road meets the next
- On/off ramps (OSM `*_link`) use the 7 m `asf3` parts whatever road they belong to
- `gis/roadgen/measure_parts.py` writes the part tables for all six families (asf1 12 m, asf2 9 m, asf3 7 m, city 10 m, grav 6 m, mud 5 m)
- Plain Python, no GDAL needed. `--dem full_dem_water.tif` pitches each part to the slope
- Import format confirmed: `"name";X;Y;yaw;pitch;roll;scale;relative height;underground flag;` (9 fields, last one `0`). Without the 9th field Terrain Builder still imports but warns "missing the underground flag". Each import makes its own object layer (`TXT_<file>_001`); importing twice = duplicates, so delete the old layer first
- Bohemia's `roads.tml` (DayZ-Samples) ships 171 of its 190 templates without bounds (`BoundingMin 999`, `AutoCenter 0`), so Terrain Builder cannot draw those objects in 2D. [`terrain/napa/TemplateLibs/roads.tml`](../terrain/napa/TemplateLibs/roads.tml) fills in the bounds of all 90 road parts measured from the p3d files (same method reproduces the 19 templates Bohemia did resolve). Bridges, sidewalks, runways and decals are left as they were
- Resolved road templates use `AutoCenter 1`: an object's position is its bounding-box centre, which is `--pivot bbox` (rows A/C of the test)
- Placement test (`terrain/napa/roads/road_test.txt`, 4 rows): row A joins up in Terrain Builder, so position = bounding-box centre (`--pivot bbox`) and yaw is clockwise (`--yaw cw`), the script defaults
- `terrain/napa/roads/napa_roads_highways.txt`: asf1 highways (2,943 parts, 57.6 km) + ramps (1,104 asf3 parts, 16 km), ready for File → Import → Objects
- In Buldozer the parts show with their real textures and follow the ground. The first import (one part at a time, 67 separate roads) had visible cracks at the joins between roads
- At Soscol Junction (CA 29 / 221 / 12) OSM has the rebuilt interchange, the 2022 photo still shows the old one, so roads and photo disagree there
- Still to check in Buldozer / in game: joins at sub-metre level, the backwards-laid left curves, and pitch on slopes (`--dem`, sign to calibrate)
- Not yet: junction pieces (`kr_*`), end pieces (`_6konec`); the two carriageways of CA 29 are 12 m parts each and may overlap where they run close

### How the Road Tool works (summary of Bohemia's wiki page "DayZ: Using Road Tool in Terrain Builder")

- Needs extracted game data on P: **plus updated road-part files** linked from that wiki page ([DayZ-Misc/Road Parts/Chernarus](https://github.com/BohemiaInteractive/DayZ-Misc/tree/master/Road%20Parts/Chernarus)), copied into `P:\DZ\structures\roads\parts` (overwrite). `gis/get_roadparts.bat` downloads all 109 (asf1/2/3, city, grav, mud, crossroads) after backing up the folder to `parts_backup`. Runway and path parts are not in that download (the extracted ones stay)
- **Window → Road types** → add a road type and give it all of one family's parts: straights (one number, e.g. `asf1_12`), corners (two numbers, e.g. `asf1_10 50`), terminator (`..._6konec`). Widths: asf1 12 m, asf2 9 m, asf3 7 m, city 10 m, grav 6 m, mud 5 m
- Select the road type → **Add road** toolbar button → double-click the map → wizard: key part type (usually the terminator), the exact part, position/rotation
- Double-click the key part → each direction (A, B, …) → **Modify** → double-click parts to chain them (straights, left/right corners). Shows in Buldozer once parts are attached
- Crossroads (`kr_t_*`, `kr_x_*`) as key parts: **Roads → Define roads and crossroads**
- **Export / Import** per key part: the chain of parts attached to a key part can be exported to a file and imported onto another key part. That file format is the way to automate: generate the part chains from the OSM lines instead of clicking them
- Bohemia recommends the tool for long stretches between settlements and placing parts by hand inside towns

Order: Hwy 29 through Napa as a test, then the other `asf1`/`asf2` roads, then town streets. The 1 m lidar already has the real road grades, so little terrain flattening should be needed.

## 4d. Ponds

`water.tml` has pond objects (`dz\water\ponds\pond_50x50.p3d`, `pond_small_*`, `pond_big_*`) for water above sea level: vineyard reservoirs and inland ponds from OSM.
