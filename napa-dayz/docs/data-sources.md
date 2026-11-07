# Data sources

| Data | Source | License | Use |
|---|---|---|---|
| Height map | USGS 3DEP 1 m DEM, [apps.nationalmap.gov/downloader](https://apps.nationalmap.gov/downloader) | Public domain | Terrain shape |
| Aerial photos | USDA NAIP, [earthexplorer.usgs.gov](https://earthexplorer.usgs.gov) (Aerial Imagery → NAIP) | Public domain | Satellite layer, surface painting (band 4 = near-infrared) |
| Roads, rivers, buildings | OpenStreetMap, Northern California extract from [Geofabrik](https://download.geofabrik.de/north-america/us/california/norcal.html) | ODbL: **must credit** | Roads, water, building outlines |
| Reference only | Google Earth, Street View | Not allowed in the map | Looking at real places |

## Files in use

### Test patch

| Data | Files |
|---|---|
| NAIP 2024 (60 cm, 4-band, EPSG:26910) | `m_3812254_nw_10_060_20240520` (lat 38.185–38.252), `m_3812246_sw_10_060_20240521` (lat 38.248–38.315) |
| USGS 1 m DEM | _tile name to be added_ |

## Credit line for the Workshop page

> Map data © OpenStreetMap contributors (ODbL). Elevation: USGS 3DEP. Imagery: USDA NAIP.

## Templates used

- World `config.cpp` layout follows Bohemia's [DayZ-Samples Test_Terrain](https://github.com/BohemiaInteractive/DayZ-Samples) (Arma and DayZ Public License Share Alike: attribution, non-commercial, share alike) and the vanilla Chernarus+ config

## Rules

- No building models taken from other games or maps. Make them, or use community packs whose authors allow reuse.
- Follow Bohemia's DayZ Tools license.
