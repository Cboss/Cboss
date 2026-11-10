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

## 5. Launch: live test server (preferred)

Boss's usual flow: publish the mod to the Steam Workshop, then load it on the private, password-protected test server in CFTools Architect.

1. **Sign the PBO** so the server can verify it: Addon Builder → Options → sign with your private key (`.biprivatekey`, made once with DayZ Tools' DS Utils). Put the matching `.bikey` in `@NapaPilot\keys\`
2. **Publish** `@NapaPilot` with DayZ Tools **Publisher**. Use **Unlisted** visibility while testing: hidden from search, but the server can still download it. A Private item may fail to download on the server
3. **Architect:** add the Workshop mod to the test server, make sure its `.bikey` lands in the server's `keys` folder, upload the `dayzOffline.NapaPilot` mission to `mpmissions`, and set the mission template to `dayzOffline.NapaPilot`
4. Keep the test server **password-protected**, with `BattlEye = 1`, `verifySignatures = 2` and `allowFilePatching = 0`

## 5b. Launch: local DayZDiag (fallback)

Run `terrain/pilot/tools/launch_napapilot.bat` (edit the three paths at the top if yours differ). It starts `DayZDiag_x64.exe` offline with `-mod` and `-mission`.

### If it stops at the main menu

`launch_napapilot.bat` reached the DayZ main menu with the mod loaded, but did not drop into the map. Use the local-server route instead:

Run `terrain/pilot/tools/launch_local_server.bat`. It starts `DayZDiag_x64.exe -server` on the NapaPilot mission (config: `serverDZ_napapilot.cfg`, same folder), waits 30 seconds, then starts a second DayZDiag as a client that joins `127.0.0.1:2302`. Server logs go to `D:\NapaMap\server_profile`.

### Server config lines that were needed

| Error | Fix in `serverDZ_napapilot.cfg` |
|---|---|
| `[Server config] :: instanceId parameter is mandatory` | `instanceId = 1;` |
| Client: "server does not accept the client's current filePatching setting" | `allowFilePatching = 1;` (local test server only, never on a public server) |

The `!!! [Inputs] Attempt to insert input twice` lines in the server window are harmless.

## If it fails

- DayZ logs are in `%LOCALAPPDATA%\DayZ`. Send the last 30 lines of the newest `.RPT` file
- Addon Builder errors: the packing log, or a screenshot

## Known gaps on the test patch

- No navmesh, so no infected or animals
- No buildings, so no loot
- Paper map shows Chernarus art; the grass-shading normal map is borrowed from Chernarus
