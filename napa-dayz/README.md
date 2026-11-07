# Napa DayZ Map

A custom DayZ terrain of Napa, California, the valley I grew up in. It covers Carneros up to Yountville and Napa County Airport across to the Silverado Trail, at 89% of real-world scale.

## Status

**Phase 1: test patch.** The 2.56 km Carneros test patch is textured with the 2024 aerial photo and shows in Buldozer. Next: world `config.cpp`, pack, and load it in DayZ.

## What's here

| Path | What it is |
|---|---|
| [`docs/map-spec.md`](docs/map-spec.md) | Map size, scale, grid, projection, the real-world area, landmark coordinates |
| [`docs/roadmap.md`](docs/roadmap.md) | Build phases as a checklist |
| [`docs/points-of-interest.md`](docs/points-of-interest.md) | Places to loot and what each one is for |
| [`docs/wine-caves.md`](docs/wine-caves.md) | Design for the keycard-locked wine cave bunkers |
| [`docs/data-sources.md`](docs/data-sources.md) | Where the map data comes from, licenses, credits |
| [`docs/terrain-builder-notes.md`](docs/terrain-builder-notes.md) | Terrain Builder steps that work, and the problems to avoid |
| [`gis/pilot_process.bat`](gis/pilot_process.bat) | GDAL commands that cut the test patch height map and satellite image |

## Tool chain

- **QGIS / GDAL:** cut, reproject and resample the USGS height data and NAIP aerial photos
- **World Machine:** edge blending, erosion and flow maps (full map only)
- **DayZ Tools:** Terrain Builder, Object Builder, Workbench, Addon Builder, Buldozer
- **Blender:** custom American buildings and the wine cave models
- **CFTools Architect:** hosting the map on the Baysic Survival Gaming servers

## What isn't stored here

Raw GIS downloads, generated images and packed files are too big for git and can be rebuilt, so `.gitignore` keeps them out. Their sources are listed in [`docs/data-sources.md`](docs/data-sources.md).
