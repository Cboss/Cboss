# Roadmap

## Phase 1: Setup and test patch ✅ done
- [x] DayZ Tools installed, P: drive mounted
- [x] QGIS, World Machine, Blender installed
- [x] Download the USGS 1 m height data and NAIP photos for the test patch
- [x] Run `gis/pilot_process.bat`
- [x] Make the Terrain Builder project `P:\NapaPilot\source\NapaPilot.tv4p` and import the height map
- [x] Connect Buldozer and see the test patch (untextured)
- [x] List the vanilla surface materials (grass: `DZ\surfaces\data\terrain\cp_grass.rvmat`)
- [x] Satellite image and surface mask, generate layers (textured test patch in Buldozer)
- [x] Export WRP, pack with Addon Builder, load the test patch in DayZ (local DayZDiag server + client, see `docs/testing-in-game.md`)
- [x] World `config.cpp`, CE files, test mission, launch script written

## Phase 2: Full terrain ✅ done
- [x] Download USGS 1 m height data for the full area (46 files)
- [x] Process to 4096 grid / 20,480 px (`gis/full_process.bat`), heights −3.76 to 725.47 m in-game
- [x] Download NAIP 2022 photos for the full area (24 tiles)
- [x] Set up `P:\Napa` (`gis/prepare_full_tb.bat`)
- [ ] (Optional, skipped for now) World Machine pass: edges, erosion and flow maps. DayZ's outside-terrain synth covers the edges; NIR covers surface painting
- [x] Terrain Builder project `P:\Napa\source\Napa.tv4p`, layers generated (13,918 files), checked in Buldozer
- [x] Full-map `config.cpp`, CE files and mission written (`terrain/napa/`)
- [x] Export WRP, pack `@Napa` (1.5 GB, signed BSG_Napa), Workshop (unlisted), running on the Architect test server

## Phase 3: Surfaces
- [x] Surface script: photo (NDVI) + OSM + height map → four surfaces (grass, forest, dirt, concrete), tested at 4.5 m
- [x] Run `gis/phase3_surfaces.bat` at full size: 13,019 roads, 32,483 buildings, 2,611 vineyards, 769 water features; grass 41%, forest 20%, dirt 31%, concrete 8%
- [ ] Regenerate the mask layers in Terrain Builder, export WRP, repack, test in game
- [ ] Later: Napa-coloured ground textures (golden grass), a 5th/6th surface if Terrain Builder's tile check allows

## Phase 4: Roads and water
- [ ] Roads from OpenStreetMap (Hwy 29, Hwy 121/12, Silverado Trail, city streets)
- [ ] Napa River, creeks, marsh edges
- [ ] Wine Train track

## Phase 5: Places to loot
- [ ] Downtown Napa / Oxbow, Napa State Hospital, Napa County Airport, Yountville, Carneros farms
- [ ] Wineries along Hwy 29 and the Silverado Trail
- [ ] Vanilla buildings as placeholders

## Phase 6: Wine cave bunkers
- [ ] Cave models (entrance front, tunnels, barrel room, tasting room)
- [ ] Keycard item and locked-door script mod
- [ ] Darkness triggers, loot points, infected

## Phase 7: Custom American buildings
- [ ] Victorian houses, ranch houses, strip mall, gas station, winery buildings, hangars
- [ ] Replace placeholders

## Phase 8: Making it playable
- [ ] AI navigation for infected and animals
- [ ] `mapgrouppos.xml`, `mapgroupproto.xml`, `cfgplayerspawnpoints.xml`, `cfgeventspawns.xml`, `types.xml`
- [ ] Mission folder `dayzOffline.napa`

## Phase 9: Ship it
- [ ] Pack with Addon Builder, sign
- [ ] Steam Workshop upload (credits OpenStreetMap)
- [ ] Add to a Baysic Survival Gaming server through CFTools Architect (test server already running the test patch, private + password)
