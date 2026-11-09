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

Plan: export the OSM roads as a guide layer in map coordinates, so the Road Tool can trace the real alignments; start with Hwy 29 through Napa as a test, then the other highways, then town streets. The 1 m lidar already has the real road grades, so little terrain flattening should be needed.

## 4d. Ponds

`water.tml` has pond objects (`dz\water\ponds\pond_50x50.p3d`, `pond_small_*`, `pond_big_*`) for water above sea level: vineyard reservoirs and inland ponds from OSM.
