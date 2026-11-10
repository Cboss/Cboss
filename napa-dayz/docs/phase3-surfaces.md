# Phase 3: surfaces

Replaces the all-grass surface mask with a real one, so grass only grows where there is grass.

## The four surfaces

| Surface | Mask colour | Material (copy of base-game) | Where |
|---|---|---|---|
| `napa_grass` | 0, 255, 0 | `cp_grass` | Open grassland, the golden hills, yards |
| `napa_forest` | 0, 110, 0 | `cp_broadleaf_sparse1` | Oak woodland, Mt. Veeder forest, creek corridors |
| `napa_dirt` | 150, 100, 50 | `cp_dirt` | Vineyards, bare fields, tracks, ponds, riverbeds, everything under sea level |
| `napa_concrete` | 128, 128, 128 | `cp_concrete1` | Paved roads, parking, runways, buildings, town |

Only four, so no Terrain Builder tile can go over the 4-materials-per-tile limit. All base-game Chernarus materials: no DLC needed. Their textures stay in `DZ\`, so grass, undergrowth and footstep sounds come from the vanilla surface definitions.

## How the mask is built (`gis/napa_surface_mask.py`)

1. **Photo** (2022 NAIP, red/green/blue/near-infrared), per pixel:
   - Forest: NDVI ≥ 0.22 and dark (mean RGB < 95)
   - Bare dirt: NDVI < 0.02, bright (≥ 150) and brown (blue at least 8 below red)
   - Pavement / roofs: NDVI < −0.04 and grey-blue (blue no more than 4 below red); dry grass has NDVI near 0 and is yellow, so it stays grass
   - Water (ponds, reservoirs): NDVI < −0.15 and near-infrared < 70 → dirt (pond bottom)
   - Everything else: grass
   - 5 × 5 majority filter to remove speckle
2. **OpenStreetMap** on top: vineyards → dirt (unless forest), water → dirt, tracks → dirt, paved roads (buffered by road class: 3–9 m half-width), parking, runways (23 m), taxiways, aprons, buildings → concrete
3. **Height map**: anything below DayZ sea level → dirt

Thresholds were tuned on the Napa photo: Mt. Veeder forest NDVI 0.33 / brightness 72; Carneros golden grass NDVI −0.01, RGB 164/161/156; downtown pavement NDVI −0.07 to −0.11 with blue above red; sewage ponds NDVI −0.35, near-infrared ~40.

Test run at 4.5 m (no OSM land use or buildings): grass 60%, forest 18%, dirt 13%, concrete 8%.

## Steps

1. Download and run `gis/phase3_surfaces.bat` from the OSGeo4W Shell:
   ```bat
   curl -L -o D:\NapaMap\gis\phase3_surfaces.bat https://raw.githubusercontent.com/Cboss/Cboss/ccr-3b451e26-3japm5/napa-dayz/gis/phase3_surfaces.bat
   D:\NapaMap\gis\phase3_surfaces.bat
   ```
   It downloads OSM into `D:\NapaMap\gis\raw\osm\`, builds `D:\NapaMap\gis\full\napa_mask.png` (+ `napa_mask_preview.png`), and updates `P:\Napa` (mask, `layers.cfg`, `config.cpp`, four `.rvmat` files)
2. Check `napa_mask_preview.png`
3. Terrain Builder, project `P:\Napa\source\Napa.tv4p`:
   - Layers manager → right-click the `napa_mask.png` layer → **Refresh content from source**
   - Mapframe Properties → Processing: layers.cfg is `P:\Napa\source\layers.cfg` (re-pick it so the four surfaces load); untick **Export satellite texture** (unchanged, saves time), tick **Export surface mask**, tick **Convert to .paa** → **Generate layers**
   - **File → Export → WRP** → `P:\Napa\world\Napa.wrp`
4. Addon Builder (same settings, `napa_exclude.lst`) → repack `@Napa` → update the Workshop item → restart the Architect test server
