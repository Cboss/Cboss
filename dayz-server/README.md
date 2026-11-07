# DayZ server config: Baysic Survival Gaming

Config files for a Baysic Survival Gaming PvE server on Chernarus, run with CFTools / Architect Manager.

Everything here is taken from Bohemia Interactive's own public files, or marked **UNVERIFIED** where no public Bohemia source covers it. See [Sources](#sources).

## What's here

```
dayz-server/
├── serverDZ.cfg                         → server root
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
| `db/globals.xml` | `CleanupLifetimeDeadPlayer` | `3600` | `7200` | Doubles how long dead player bodies stay. The time unit isn't stated in Bohemia's files. |
| `cfgeconomycore.xml` | `<ce folder="custom">` | none | added | Loads `custom/types_custom.xml` for mod loot. **UNVERIFIED syntax.** |
| `db/messages.xml` | messages | none | 3 | Welcome, rules and base reminders, using the tags documented in the comments of Bohemia's vanilla `messages.xml` |

`cfggameplay.json` is only used when `enableCfgGameplayFile = 1` is set in `serverDZ.cfg` and the file exists in the mission. Otherwise the server reads those settings from `serverDZ.cfg` instead (`cfggameplayhandler.c`, `LoadData`).

Vanilla DayZ has no PvP switch in these files: the damage settings protect bases and storage, not players.

## Still to verify

The server program reads these directly, so they aren't in any public Bohemia repo. Check each one against the stock `serverDZ.cfg` that came with your server install, or against [DayZ:Server_Configuration](https://community.bistudio.com/wiki/DayZ:Server_Configuration) in a browser:

- every `serverDZ.cfg` line tagged `[UNVERIFIED]`
- the `<ce folder>` block in `cfgeconomycore.xml` ([DayZ:Central_Economy_mission_files_modding](https://community.bistudio.com/wiki/DayZ:Central_Economy_mission_files_modding))
- the ports for each instance: use the ones Architect assigns, and forward exactly those on pfSense

## Before you deploy

1. **Passwords.** `serverDZ.cfg` keeps `passwordAdmin = "CHANGE_ME"` because this repo is public. Set the real one on the server or in Architect, never in a commit. The validator fails if a real password shows up here.
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
- The Bohemia wiki pages above could not be read from the automated environment that built these files. Anything that only they cover is marked UNVERIFIED.

## License

The mission files are adapted from Bohemia Interactive's DayZ-Central-Economy, which is licensed under the [Arma and DayZ Public License Share Alike (ADPL-SA)](https://www.bohemia.net/community/licenses/arma-and-dayz-public-license-share-alike-adpl-sa): attribution, **non-commercial**, Arma and DayZ only, share alike. These adapted files are shared under the same license. © Bohemia Interactive a.s.; DAYZ® is a registered trademark of Bohemia Interactive a.s.
