# Wine cave bunkers

Napa wine caves really are dug into the hillsides, so they make natural DayZ bunkers. There are 3–5 of them, locked with a keycard, holding the best loot on the map.

## Building them

1. At each site, lower the ground into a cut in the hillside.
2. Place a custom hillside model there with the tunnels built inside it. The hill above the cave is part of the model, not the terrain.
3. Model the pieces in Blender / Object Builder: entrance front, tunnel sections, barrel room, tasting room. Each needs the usual LODs (view, fire, collision, paths for AI).
4. Make the inside pitch dark with `cfgundergroundtriggers.json` in the mission folder (the same system Livonia's bunker uses), so players need a light.
5. Loot points go in `mapgroupproto.xml`. A few infected inside.

## Keycard

Small script mod, modeled on how Livonia's bunker door and punched card work.

| Piece | Plan |
|---|---|
| Item | `Napa_CaveKeycard` |
| Where it spawns | Napa State Hospital, Napa County Airport, rarely on infected security guards |
| `types.xml` | Low spawn count, so cards are rare |
| Door | Only opens when the player is holding a card |
| Wear | Each use damages the card, so about 3–4 uses per card |
| Auto-close | Door closes again after a few minutes, so nobody can follow you in for free |

## Open questions

- One card type for every cave, or a different card per cave?
- Cave names (all made-up winery names)
- Exact cave sites: hillsides near the Silverado Trail, Carneros and the Mt. Veeder slopes are good candidates
