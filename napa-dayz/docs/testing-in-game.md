# Testing the test patch in DayZ

Getting the Carneros test patch from Terrain Builder into the real game.

Files referred to here are in [`terrain/pilot/`](../terrain/pilot/).

## 1. Export the world from Terrain Builder

1. `mkdir P:\NapaPilot\world`
2. **File → Export → WRP...** → `P:\NapaPilot\world\NapaPilot.wrp`
3. Check the file is a few MB, not 0 KB

## 2. Put the mod files on P:

| From the repo | To |
|---|---|
| `terrain/pilot/config.cpp` | `P:\NapaPilot\config.cpp` |
| `terrain/pilot/ce\*.xml` | `P:\NapaPilot\ce\` |

Already there from earlier steps: `P:\NapaPilot\data\napa_grass.rvmat`, `P:\NapaPilot\data\layers\` (generated), `P:\NapaPilot\world\NapaPilot.wrp`.

## 3. Pack it with Addon Builder

DayZ Tools launcher → **Addon Builder**:

| Setting | Value |
|---|---|
| Addon source directory | `P:\NapaPilot` |
| Destination directory | `D:\NapaMap\@NapaPilot\addons` |
| Options → Addon prefix | `NapaPilot` |
| Options → Binarize | On |
| Options → Clear temp folder | On |

Click **Pack**. Result: `D:\NapaMap\@NapaPilot\addons\NapaPilot.pbo`. No signing needed for offline testing.

The `source` folder (Terrain Builder project and big PNGs) gets packed too. That only makes the PBO bigger; it can be excluded later.

## 4. Make the test mission

1. In `D:\Steam\steamapps\common\DayZ\Missions`, copy `dayzOffline.chernarusplus` and name the copy **`dayzOffline.NapaPilot`**. The part after the dot must match the world class name in `config.cpp`
2. Overwrite these four files in the copy with the ones from `terrain/pilot/mission/dayzOffline.NapaPilot/`:
   - `cfgplayerspawnpoints.xml`: spawn areas inside the 2560 m patch
   - `cfgeventspawns.xml`: empty (no Chernarus vehicles or heli crashes)
   - `cfgenvironment.xml`: no infected or animal territories (no navmesh yet)
   - `mapgrouppos.xml`: empty (no buildings, so no loot positions)
3. If the copy has a `storage_1` folder, delete it. It holds the old Chernarus save

## 5. Launch

Run `terrain/pilot/tools/launch_napapilot.bat` (edit the three paths at the top if yours differ). It starts `DayZDiag_x64.exe` offline with `-mod` and `-mission`.

## If it fails

- DayZ logs are in `%LOCALAPPDATA%\DayZ`. Send the last 30 lines of the newest `.RPT` file
- Addon Builder errors: the packing log, or a screenshot

## Known gaps on the test patch

- No navmesh, so no infected or animals
- No buildings, so no loot
- Paper map shows Chernarus art; the grass-shading normal map is borrowed from Chernarus
