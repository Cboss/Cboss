# Napa DayZ Map

A custom DayZ terrain of Napa, California, the valley I grew up in. It covers Carneros up to Yountville and Napa County Airport across to the Silverado Trail, at 89% of real-world scale.

## Status

**Phase 2 done.** The full 20.48 km map (1 m USGS lidar from five surveys, 2022 NAIP photo, river and bay marsh at sea level) runs on the Architect test server from an unlisted Workshop item. Next: Phase 3, surfaces (ground textures and grass).

## What's here

| Path | What it is |
|---|---|
| [`docs/map-spec.md`](docs/map-spec.md) | Map size, scale, grid, projection, the real-world area, landmark coordinates |
| [`docs/roadmap.md`](docs/roadmap.md) | Build phases as a checklist |
| [`docs/points-of-interest.md`](docs/points-of-interest.md) | Places to loot and what each one is for |
| [`docs/wine-caves.md`](docs/wine-caves.md) | Design for the keycard-locked wine cave bunkers |
| [`docs/data-sources.md`](docs/data-sources.md) | Where the map data comes from, licenses, credits |
| [`docs/terrain-builder-notes.md`](docs/terrain-builder-notes.md) | Terrain Builder steps that work, and the problems to avoid |
| [`docs/testing-in-game.md`](docs/testing-in-game.md) | Export, pack and launch the test patch in DayZ |
| [`docs/phase2-full-terrain.md`](docs/phase2-full-terrain.md) | Full-map downloads, processing, Terrain Builder settings |
| [`gis/full_process.bat`](gis/full_process.bat) | GDAL commands for the full 20.48 km height map and satellite image |
| [`gis/prepare_full_tb.bat`](gis/prepare_full_tb.bat) | Sets up `P:\Napa` for the full-map Terrain Builder project |
| [`terrain/napa/`](terrain/napa/) | Full-map files: `layers.cfg`, world `config.cpp`, CE files, mission files |
| [`docs/phase3-surfaces.md`](docs/phase3-surfaces.md) | Surface mask: four ground types from the photo + OSM |
| [`docs/phase4-roads-water.md`](docs/phase4-roads-water.md) | Smart water, object libraries, roads, ponds |
| [`gis/phase3_surfaces.bat`](gis/phase3_surfaces.bat) + [`gis/napa_surface_mask.py`](gis/napa_surface_mask.py) | Downloads OSM, builds the surface mask, updates `P:\Napa` |
| [`terrain/pilot/`](terrain/pilot/) | Test patch files: `layers.cfg`, world `config.cpp`, CE files, test mission, launch script |
| [`gis/pilot_process.bat`](gis/pilot_process.bat) | GDAL commands that cut the test patch height map and satellite image |

## Tool chain

- **QGIS / GDAL:** cut, reproject and resample the USGS height data and NAIP aerial photos
- **World Machine:** edge blending, erosion and flow maps (full map only)
- **DayZ Tools:** Terrain Builder, Object Builder, Workbench, Addon Builder, Buldozer
- **Blender:** custom American buildings and the wine cave models
- **CFTools Architect:** hosting the map on the Baysic Survival Gaming servers

## What isn't stored here

Raw GIS downloads, generated images and packed files are too big for git and can be rebuilt, so `.gitignore` keeps them out. Their sources are listed in [`docs/data-sources.md`](docs/data-sources.md).
