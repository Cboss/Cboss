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

Order: Hwy 29 through Napa as a test, then the other `asf1`/`asf2` roads, then town streets. The 1 m lidar already has the real road grades, so little terrain flattening should be needed.

## 4d. Ponds

`water.tml` has pond objects (`dz\water\ponds\pond_50x50.p3d`, `pond_small_*`, `pond_big_*`) for water above sea level: vineyard reservoirs and inland ponds from OSM.
