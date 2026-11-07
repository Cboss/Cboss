# DayZ server config: Baysic Survival Gaming

Config files for a Baysic Survival Gaming PvE server on Chernarus, run with CFTools / Architect Manager. They start from Bohemia's current vanilla mission files, and every change from vanilla is listed below so it's easy to see what this server does differently.

## What's here

```
dayz-server/
├── serverDZ.cfg                         → server root, next to DayZServer_x64.exe
├── mpmissions/dayzOffline.chernarusplus/  → <server>/mpmissions/dayzOffline.chernarusplus/
│   ├── cfgeconomycore.xml               vanilla + registers the custom/ loot folder
│   ├── cfggameplay.json                 vanilla + PvE damage settings
│   ├── db/globals.xml                   vanilla + longer body cleanup
│   ├── db/messages.xml                  welcome + rules messages
│   └── custom/types_custom.xml          loot entries for mod items (empty to start)
└── tools/validate.py                    checks everything before it goes on the server
```

Only the files that differ from vanilla live here. The rest of the mission folder (`db/types.xml`, `db/events.xml`, `init.c`, map groups and so on) comes from the server install as-is.

## Changes from vanilla

| File | Setting | Vanilla | Here | Why |
|---|---|---|---|---|
| `cfggameplay.json` | `disableBaseDamage` | `false` | `true` | PvE: bases can't be raided |
| `cfggameplay.json` | `disableContainerDamage` | `false` | `true` | PvE: tents, barrels and crates can't be destroyed |
| `db/globals.xml` | `CleanupLifetimeDeadPlayer` | `3600` | `7200` | 2 hours to get back to your body instead of 1 |
| `cfgeconomycore.xml` | `<ce folder="custom">` | none | added | Mod loot goes in its own file, not mixed into `db/types.xml` |
| `db/messages.xml` | messages | none | 3 | Welcome message, rules reminder, base-building reminder |

Vanilla DayZ has no "PvP off" switch, so the damage toggles stop raiding but not player killing. A rules-and-admin approach covers the rest, or a mod with PvE zones if you want it enforced in-game.

## Before you deploy

1. **Passwords.** `serverDZ.cfg` keeps `passwordAdmin = "CHANGE_ME"` because this repo is public. Set the real one on the server or in Architect, never in a commit. The validator fails the check if a real password shows up here.
2. **One `instanceId` per server.** With 4+ servers on one host, each needs its own `instanceId`, game port and query port, or they'll fight over persistence and ports.
3. **Map.** For Livonia, Sakhal and other maps, change `template` in `serverDZ.cfg` and rename the mission folder to match (`dayzOffline.enoch`, `dayzOffline.sakhal`, …). Rebuild the files from that map's vanilla set, because temperatures and spawns differ per map.
4. **Restarts.** Let Architect's scheduler handle restarts and countdowns. `messages.xml` deliberately has no `<shutdown>` message, which would start a second timer of its own.

## Validate before every upload

```bash
python3 dayz-server/tools/validate.py
```

Point it at a live server folder to also check the full `db/types.xml` against the custom files:

```bash
python3 dayz-server/tools/validate.py "D:\DayZServer"
```

It checks for:

- XML that won't parse (one bad tag and the server ignores the whole file)
- JSON with comments or trailing commas (DayZ wants strict JSON)
- `serverDZ.cfg` lines missing their `;`, and real passwords
- loot entries with `min` above `nominal` or `quantmin` above `quantmax`
- the same item defined in two files
- custom files listed in `cfgeconomycore.xml` that don't exist

The same check runs on GitHub for every push that touches `dayz-server/`.

## Adding mod loot

1. Copy the mod's `<type>` entries from its own `types.xml` into `custom/types_custom.xml`.
2. If the mod adds its own categories or usage flags, add them to `cfglimitsdefinitionuser.xml`.
3. Run the validator, upload, and restart.
4. To change a **vanilla** item, edit `db/types.xml` on the server, not the custom file, so each item is only defined once.

## Firewall (pfSense)

On the Netgate, forward these to the DayZ host on the server VLAN, one set per instance:

| Purpose | Default | Protocol |
|---|---|---|
| Game | 2302 (the server also uses the next few ports, so forward 2302–2305) | UDP |
| Steam query (server browser) | 27016, from `steamQueryPort` | UDP |
| BattlEye RCon (CFTools Cloud uses it) | `RConPort` in `battleye/BEServer_x64.cfg` | UDP |

Give each extra server its own block with no overlap, for example 2402–2405 / 27017 for server 2. If CFTools publishes the addresses it connects from, limit the RCon rule's source to them, because RCon on the open internet is a common target.
