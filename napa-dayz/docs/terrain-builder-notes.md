# Terrain Builder notes

What worked for the Carneros test patch, in order, plus the problems hit along the way. Use this for the full 20 km map.

## Setup that has to be right first

| Item | Setting |
|---|---|
| Game data | DayZ Tools launcher → **Extract Game Data** to P:. `P:\DZ` must exist before any `.rvmat` can be found |
| Game path | DayZ Tools launcher → Settings → untick **Default**, browse to the real DayZ folder (`D:\Steam\steamapps\common\DayZ`), **Apply**. With Default ticked, Terrain Builder still looked on C: for Buldozer |
| Buldozer profile folder | `P:\Buldozer` must exist |
| Start Terrain Builder | From the **DayZ Tools launcher**, not a shortcut |

## Project steps that work

1. **File → New Project.** Save As is greyed out until the project has something in it.
2. **Mapframes → Add mapframe**, keep UTM zone **31 N**.
3. Mapframe **Properties**:
   - **Location:** name, output root `P:\NapaPilot\data\`, Easting `200000`, Northing `0`
   - **Samplers:** grid `512 × 512`, cell `5` (2560 m), image `2560 × 2560` (1 m/px), tile `512`, overlap `64`
   - **Processing:** layers.cfg path. **OK** stays greyed out until layers.cfg loads, and layers.cfg only loads if every `.rvmat` it names exists
4. **File → Save Project As** → `P:\NapaPilot\source\NapaPilot.tv4p`
5. **File → Import → Terrain** → `pilot_dem.asc`. The `.prj` next to it must say **UTM 31N** (`gdal_translate -a_srs EPSG:32631`), or the import is refused ("from another zone than project zone")
6. Import the satellite image and surface mask
7. Mapframe **Properties → Processing → Rebuild terrain**. An import alone only adds a source raster layer; Rebuild terrain copies it into the mapframe's heightfield. Skip it and Buldozer shows only water
8. Processing: tick **Export satellite texture**, **Export surface mask** (4 materials per cell), **Convert to .paa** → **Generate layers**. Without generated layers Buldozer crashes at "Texturing surface…"
9. Select the mapframe in the **Mapframes** panel → start Buldozer

## Things to avoid

- **Dragging the blue mapframe border** in the 2D view. It moves or resizes the mapframe and rewrites cell size and origin (it ended up 16 m with cell size 0.031)
- **Duplicate mapframes.** Two mapframes with the same name left no "active" mapframe, so Buldozer refused to connect. Starting a clean project fixed it
- **Renaming project files in Explorer.** The `.tv4p` refers to its `.v4d` and folders by name; use Save As
- **Create a config / internal MCE** buttons: they fail ("Unable to run MapConfigEditor.bat") and aren't needed

## Known look issues (for later)

- Buildings, cars, tree shadows and solar panels are painted into the NAIP photo. Up close they show as flat smears. When real 3D buildings and trees go in, clean or blur the satellite image under them
- Surface mask is one material (grass) everywhere. Phase 3 adds vineyard, dry hillside, asphalt and so on
