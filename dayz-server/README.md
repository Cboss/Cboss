# DayZ server config: Baysic Survival Gaming

Config files for Baysic Survival Gaming servers run with CFTools / Architect Manager: a PvE server on Chernarus, and a PvPvE server on Sahrani Plus (see [Originals and masters](#originals-and-masters)).

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
├── originals/                           files exactly as received, never edited (see below)
│   ├── vanilla-chernarusplus/           Bohemia's vanilla files + VERSIONS.md
│   └── sahrani-plus/                    the map's mission files, db/, env/, types/ and CustomTypes/<mod>/, each folder with VERSIONS.md
├── sahrani-plus/                        Sahrani Plus PvPvE server
│   ├── masters.json                     recipe: our changes + Boss's conflict decisions
│   ├── mission/                         built masters, only the files we change (don't edit by hand)
│   └── MERGE_REPORT.md                  what the last build did (built)
└── tools/
    ├── validate.py                      checks everything before it goes on the server
    ├── add_original.py                  stores a new version of an original file
    ├── build_masters.py                 builds every master from originals + recipe
    └── merge_entries.py                 entry-by-entry merge used by build_masters.py
```

Only the files that differ from vanilla live here. The rest of the mission folder (`db/types.xml`, `db/events.xml`, `init.c`, map groups and so on) comes from the server install as-is.

## Originals and masters

Map and mod files change, so our edits are never made inside them. Three rules keep updates cheap:

1. **Originals are stored as-is.** Every file from a map author, a mod or Bohemia goes into `originals/<source>/` byte for byte, with its line endings untouched, and gets a row in that folder's `VERSIONS.md` (date, sha256, line count, where it came from). A new version replaces the old file in the same commit, and git keeps every older version.
2. **Our changes live in the recipe, not in the files.** `sahrani-plus/masters.json` lists every change we make, with the reason, and every conflict decision.
3. **Masters are built by script.** `tools/build_masters.py` rebuilds each master from the originals and the recipe. Masters are never edited by hand, so the same inputs always give the same output.

`sahrani-plus/mission/` holds only the files we change. Everything else on the server is the original as the author ships it. `validate.py` checks the two together: a master's references are looked up in `mission/` first, then in `originals/sahrani-plus/` (the recipe's `base`). Once the instance's `serverDZ.cfg` gives the mission folder name (its `template=` line), the folder can be renamed to match.

### Three kinds of master

| Type | Used for | What it does |
|---|---|---|
| `merge` | `mapclusterproto.xml`, `db/events.xml` | Entry by entry (`<export>`, `<cluster>`, `<event>`). Keeps every line of the map's file in order. Copies vanilla entries in character for character between `build_masters.py` comments (`add_vanilla`: `"all"` or a list). Removes map entries listed in `drop_map`, leaving a comment with the reason. Swaps map events listed in `replace_map` for a new name and child list, keeping the event's own settings (used to turn the dino events into real animals). An entry in both files that differs is a **conflict**: the map's version stays until a decision says otherwise. `prefer` sets a default for a whole file. |
| `patch` | `serverDZ.cfg` | Exact text edits. Each `find` must occur exactly once in the original. If an update changes that text, the build stops and names the edit, so nothing gets silently lost. |
| `copy` | `cfgenvironment.xml` | An original used unchanged, such as a vanilla file in place of the map's. |

Before writing anything, the script checks that every master is well-formed. For merges, it also checks that no map line was lost or reordered, that every entry is present exactly once, and that each copied entry matches its source exactly. If any check fails, nothing is written. `MERGE_REPORT.md` lists the input hashes, every change and why, every conflict with both versions side by side, and recipe lines that no longer apply after an update.

### When an updated file arrives

```bash
# 1. Store it exactly as received; prints what changed since the last version
python3 dayz-server/tools/add_original.py sahrani-plus path/to/mapclusterproto.xml --note "workshop update 2026-12-01"
#    (sahrani-plus/db, sahrani-plus/env, sahrani-plus/types, sahrani-plus/CustomTypes/BRDK ... for subfolders)

# 2. Rebuild the masters; prints conflicts still waiting on a decision
python3 dayz-server/tools/build_masters.py build dayz-server/sahrani-plus/masters.json

# 3. Validate, then commit the original, masters and report together
python3 dayz-server/tools/validate.py
```

To compare two versions of `mapclusterproto.xml` or `events.xml` entry by entry:

```bash
python3 dayz-server/tools/merge_entries.py old.xml new.xml
```

### Deciding a conflict

Read the conflict in `MERGE_REPORT.md`, add a decision to that master's `decisions` in `masters.json`, then rebuild:

```json
"decisions": {
  "export:AppleTree2": {"keep": "map", "why": "author switched to the summer tree model"},
  "cluster:FagusSylvatica_2d": {"keep": "vanilla", "why": "..."}
}
```

`keep` is `map` or `vanilla`. `check --strict` fails while any conflict is undecided.

GitHub runs `build_masters.py check` on every push. It fails if a committed master or report doesn't match what the script builds from the committed originals, which catches hand edits and forgotten rebuilds.

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
- stray text after a tag (like `<pos .../>sa`), which parses but is always a typo
- `cfgenvironment.xml` loading `env/` files that don't exist or differ only in letter case (Linux servers care), territories using a file nothing loads, and `env/` files nothing loads

Files under `originals/` are kept exactly as received, so problems in them are reported as warnings, not errors. Fix them in our own copy, never in the original.

Tested against Bohemia's full vanilla Chernarus mission (2,382 loot types): 0 errors, 0 warnings. The same check runs on GitHub for every push that touches `dayz-server/`.

## Sources

- [BohemiaInteractive/DayZ-Central-Economy](https://github.com/BohemiaInteractive/DayZ-Central-Economy): vanilla mission files these are built from
- [BohemiaInteractive/DayZ-Script-Diff](https://github.com/BohemiaInteractive/DayZ-Script-Diff): game scripts, used to confirm what the `cfggameplay.json` and `serverDZ.cfg` settings do
- The live Napa `serverDZ.cfg` (generated by CFTools Architect): setting names, file layout and house values
- The Bohemia wiki pages above could not be read from the automated environment that built these files. Anything that only they cover is marked UNVERIFIED.

## License

The mission files are adapted from Bohemia Interactive's DayZ-Central-Economy, which is licensed under the [Arma and DayZ Public License Share Alike (ADPL-SA)](https://www.bohemia.net/community/licenses/arma-and-dayz-public-license-share-alike-adpl-sa): attribution, **non-commercial**, Arma and DayZ only, share alike. These adapted files are shared under the same license. © Bohemia Interactive a.s.; DAYZ® is a registered trademark of Bohemia Interactive a.s.
