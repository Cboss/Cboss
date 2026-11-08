# DayZ server config: Baysic Survival Gaming

Config files for a Baysic Survival Gaming PvE server on Chernarus, run with CFTools / Architect Manager.

Everything here comes from one of three sources: Bohemia Interactive's public files, the game's own scripts, or a live Baysic server config. Anything none of them covers is marked **UNVERIFIED**. See [Sources](#sources).

## What's here

```
dayz-server/
├── serverDZ.cfg                         → server root (same layout as the live Napa server)
├── mpmissions/dayzOffline.chernarusplus/  → <server>/mpmissions/dayzOffline.chernarusplus/
│   ├── cfgeconomycore.xml               vanilla + custom loot folder (UNVERIFIED syntax)
│   ├── cfggameplay.json                 vanilla + PvE damage settings
│   ├── db/globals.xml                   vanilla + longer dead-player cleanup
│   ├── db/messages.xml                  welcome + rules messages
│   └── custom/types_custom.xml          loot entries for mod items (empty to start)
└── tools/validate.py                    checks everything before it goes on the server
```

Only the files that differ from vanilla live here. The rest of the mission folder (`db/types.xml`, `db/events.xml`, `init.c`, map groups and so on) comes from the server install as-is.

## Changes from vanilla

The vanilla values come from Bohemia's DayZ-Central-Economy repo (commit `f220b29`, October 16, 2026).

| File | Setting | Vanilla | Here | What it does (source) |
|---|---|---|---|---|
| `cfggameplay.json` | `disableBaseDamage` | `false` | `true` | Base-building parts can't be damaged (`basebuildingbase.c` → `entityai.c` `ProcessInvulnerabilityCheck`) |
| `cfggameplay.json` | `disableContainerDamage` | `false` | `true` | Containers, tents and barrels with holes can't be damaged (`container_base.c`, `tentbase.c`, `barrelholes_colorbase.c`) |
| `cfggameplay.json` | `disablePersonalLight` | `false` | `true` | Matches the live Napa server's `disablePersonalLight=1` |
| `cfggameplay.json` | `lightingConfig` | `0` | `1` | Matches the live Napa server's `lightingConfig=1` |
| `db/globals.xml` | `CleanupLifetimeDeadPlayer` | `3600` | `7200` | Doubles how long dead player bodies stay. The time unit isn't stated in Bohemia's files. |
| `cfgeconomycore.xml` | `<ce folder="custom">` | none | added | Loads `custom/types_custom.xml` for mod loot. **UNVERIFIED syntax.** |
| `db/messages.xml` | messages | none | 3 | Welcome, rules and base reminders, using the tags documented in the comments of Bohemia's vanilla `messages.xml` |

`cfggameplay.json` is only used when `enableCfgGameplayFile=1` is set in `serverDZ.cfg` and the file exists in the mission. Otherwise the server reads those settings from `serverDZ.cfg` instead (`cfggameplayhandler.c`, `LoadData`). The lighting values match in both files, so they stay the same whichever file is in use.

**Live servers:** the Napa `serverDZ.cfg` has no `enableCfgGameplayFile` line. The script only loads `cfggameplay.json` when that setting is on, so unless the server treats a missing setting as on, Napa ignores its `cfggameplay.json`. What the server does with a missing setting isn't visible in the scripts. Check before relying on any edits to that file.

Vanilla DayZ has no PvP switch in these files: the damage settings protect bases and storage, not players.

## serverDZ.cfg

The template copies the live Napa server's file exactly: same settings, same order, same `key=value;` style with no spaces or comments. Only the server-specific values change: `hostname`, `description` and `template`. Six settings the game scripts read are added at the end.

| Setting | Source |
|---|---|
| Everything from `hostname` to `respawnTime` | Live Napa `serverDZ.cfg` (CFTools Architect) |
| `enableCfgGameplayFile` | `cfggameplayhandler.c` |
| `adminLogPlayerHitsOnly`, `adminLogPlacement`, `adminLogBuildActions`, `adminLogPlayerList` | `pluginadminlog.c`, whose comments say: hits only vs. all hits; trap and tent placement; build, dismantle and destroy actions; player list with positions every 5 minutes |
| `enableDebugMonitor` | `missionserver.c` |

Per server, change `hostname`, `description`, `instanceId`, `steamQueryPort` and `template`. The values `shardId="123abc"` and `steamQueryPort=27015` are copied from Napa, so set the right ones for each instance.

## Still to verify

- The `<ce folder>` block in `cfgeconomycore.xml` ([DayZ:Central_Economy_mission_files_modding](https://community.bistudio.com/wiki/DayZ:Central_Economy_mission_files_modding)). After the first boot, confirm in the server log that `types_custom.xml` loads.
- Game ports for each instance: use the ones Architect assigns, and forward exactly those on pfSense.

## Before you deploy

1. **Passwords.** `password` and `passwordAdmin` stay blank in this repo because it's public, the same as in the live Napa file. Set the real values on the server or in Architect, never in a commit. The validator fails if a real password shows up here.
2. **Map.** Bohemia's mission folders for other maps are `dayzOffline.enoch` (Livonia), `dayzOffline.sakhal` and `dayzOffline.nasdara`. Change `template` in `serverDZ.cfg` to match, and rebuild from that map's vanilla files, because their `cfggameplay.json` temperatures differ.
3. **Restarts.** Leave restarts and countdowns to Architect's scheduler. Per Bohemia's notes in the vanilla `messages.xml`, a `<shutdown>` message counts down from server start, so it would run alongside Architect's schedule.

## Validate before every upload

```bash
python3 dayz-server/tools/validate.py
```

Point it at a live server folder to also check the full `db/types.xml` against the custom files:

```bash
python3 dayz-server/tools/validate.py "D:\DayZServer"
```

It checks for:

- XML that won't parse
- JSON that isn't strict JSON (comments, trailing commas)
- `serverDZ.cfg` lines missing their `;`, and real passwords
- loot entries with `min` above `nominal` (when `nominal` is above 0) or `quantmin` above `quantmax`
- the same item defined in two files
- custom files listed in `cfgeconomycore.xml` that don't exist

Tested against Bohemia's full vanilla Chernarus mission (2,382 loot types): 0 errors, 0 warnings. The same check runs on GitHub for every push that touches `dayz-server/`.

## Sources

- [BohemiaInteractive/DayZ-Central-Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy): vanilla mission files these are built from
- [BohemiaInteractive/DayZ-Script-Diff](https://github.com/BohemiaInteractive/DayZ-Script-Diff): game scripts, used to confirm what the `cfggameplay.json` and `serverDZ.cfg` settings do
- The live Napa `serverDZ.cfg` (generated by CFTools Architect): setting names, file layout and house values
- The Bohemia wiki pages above could not be read from the automated environment that built these files. Anything that only they cover is marked UNVERIFIED.

## License

The mission files are adapted from Bohemia Interactive's DayZ-Central-Economy, which is licensed under the [Arma and DayZ Public License Share Alike (ADPL-SA)](https://www.bohemia.net/community/licenses/arma-and-dayz-public-license-share-alike-adpl-sa): attribution, **non-commercial**, Arma and DayZ only, share alike. These adapted files are shared under the same license. © Bohemia Interactive a.s.; DAYZ® is a registered trademark of Bohemia Interactive a.s.
