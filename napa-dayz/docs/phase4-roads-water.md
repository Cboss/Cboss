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

### Plan B: road parts generated from the guide

The Road Tool refused to add roads ("Area tool - Couldn't use 'add Area' the target layer is locked", although no layer was locked). In the game roads are just objects, so two scripts do the Road Tool's job.

**What Buldozer taught us**

- Terrain Builder's object text format: `"name";X;Y;yaw;pitch;roll;scale;relative height;underground flag;` (9 fields, last one `0`). Each import makes its own object layer (`TXT_<file>_001`); delete that layer before importing again
- An object's position is its bounding-box centre and yaw is clockwise (placement test `terrain/napa/roads/road_test.txt`, row A)
- Bohemia's `roads.tml` ships 171 of 190 templates without bounds, so they draw nothing in 2D: use [`terrain/napa/TemplateLibs/roads.tml`](../terrain/napa/TemplateLibs/roads.tml). **View → View scene objects** must be on
- **The game sets a road part on the ground by its corner points only.** Curves have a row of points every ~2 m and follow the ground; a straight has four corners and is a flat sheet between its ends. Wherever the raw lidar ground rises in between (a bump, a river bank, the edge of an overpass, a culvert) it pokes through and the road shows a hole: rectangles, triangles and bow-ties, often on both carriageways at the same spot. Holes were first blamed on the 12.5 m straight (wrong: one sat between two plain 25 m straights at First Street)
- So parts are written flat (pitch 0) and the ground under the roads has to be graded

**1. Road bed: `gis/napa_road_bed.py`** (numpy + GDAL, about a minute)

- Roads are done biggest first: highways (12 m), ramps (7 m), main roads (9 m), two-lane roads (7 m), streets (10 m), tracks (6 m). A smaller road is pinned to a bigger road's bed where it meets or runs beside it (at-grade crossing, at most 15% ramp) and never changes it
- Water stays open: where a road crosses 15–300 m of sea-level water the ground is not touched, the road parts stop at each bank and the crossing is listed in `napa_bridges.csv` (a bridge to build). Water narrower than 15 m gets a culvert fill; more than 300 m of water along a road is a levee or marsh track and is raised to at least 1.5 m. Open water is frozen: no road bed changes it except those fills (the first version raised a causeway across the Napa River, which blocked the river)
- Per road: ground height every 2.5 m along the centre line → narrow dry dips filled (80 m for highways down to 20 m for tracks: creeks, the gap a removed bridge deck leaves) → smoothed (60 m down to 20 m) → kept within a fill/cut limit of the natural ground (8 / 3 m for highways down to 3 / 2 m for tracks)
- The grid is set to the weighted mean of the profile heights around each point out to road half-width + 5.1 m, so the bed is level across the road and neighbouring beds (the two carriageways of CA 29, crossing streets) merge without a step; then blended into the natural ground over 10 m. No grid point moves more than the limit + 1.5 m
- Overpasses become at-grade crossings for now. River and slough bridges are gaps in the road until bridge objects are placed (next step)
- Prints three check points (flat bed spots that moved more than 1 m) with the Elevation Terrain Builder should show there
- Prints the five biggest fills and cuts with their in-game coordinates, to look at in Buldozer
- Test on a stand-in height map (20 m data blown up to 5 m with lidar-like noise): 25 m highway straights with ground poking through more than 5 cm: 1,235 of 1,750 before, 29 after

**2. Road parts: `gis/napa_road_objects.py`** (plain Python; GDAL only for `--dem`)

- Part geometry in `gis/roadgen/road_parts_<family>.csv` (asf1 12 m, asf2 9 m, asf3 7 m, city 10 m, grav 6 m, mud 5 m), measured from Bohemia's p3d files by `gis/roadgen/measure_parts.py` / `mlod.py` (memory points `LB`/`PB` begin, `LE`/`PE` end). Origin = begin centre, road along +Z, curves turn right; a curve laid backwards turns left. `asf1_12` is 12.5 m long, `asf1_25` 25 m, `asf1_6` 6.25 m
- Joins OSM lines into whole roads: at each node the ends are paired straightest-first (within 30°), so a highway runs through the points where ramps leave it. All asf1 becomes 4 long roads
- Chooses parts with a beam search (looks ahead, keeps the 10 best partial roads per 5 m): parts sit a median 0.06 m off the OSM line, 99% within 1.1 m
- Each road runs to its very end (may overshoot up to 7 m); on/off ramps (OSM `*_link`) use the 7 m `asf3` parts
- With `--dem full_dem_roads.tif` the road is cut wherever the ground is sea-level water (a bridge gap: parts stop 1 m back from the last dry point and never overshoot), and a straight is only laid where the ground rises less than 5 cm above it between its ends; otherwise a shorter straight or a curve part is used. On the graded test terrain: 1 of 1,699 highway straights left above 5 cm (0.06 m)
- The 12.5 m straights (`*_12`) are left out (`SKIP_SUFFIXES`): they do not show in Buldozer. On the graded bed at the Napa River bridge approach (14062 / 4520) both carriageways had a clean 12.5 m gap exactly where each had an `asf1_12`. So there were two causes of holes: this part, and ground poking through long straights
- Not yet: junction pieces (`kr_*`), end pieces (`_6konec`)
- At Soscol Junction (CA 29 / 221 / 12) OSM has the rebuilt interchange, the 2022 photo still shows the old one, so roads and photo disagree there

**Steps:** OSGeo4W Shell →
```bat
curl -L -o D:\NapaMap\gis\phase4_roads.bat https://raw.githubusercontent.com/Cboss/Cboss/ccr-3b451e26-3japm5/napa-dayz/gis/phase4_roads.bat
D:\NapaMap\gis\phase4_roads.bat
```
Then Terrain Builder: **File → Import → Terrains** → `source\\napa_dem.asc` ("Refresh content from source" did not load the new heights properly: the highway read −0.13 m where the file had +1.5 m) → mapframe Properties → Processing → **Rebuild terrain** → hover over the script's check points → Objects tab: delete the old `TXT_napa_roads_highways_001` layer → **File → Import → Objects** → `source\roads\napa_roads_highways.txt` → Save → Buldozer.

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
