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

## Replacing a source image (mask, satellite, height map)

- **"Refresh content from source" did not pick up a new `napa_mask.png`** (Phase 3). Fix: right-click the layer → **Remove this Terrain**, import the file again, check **Terrain coordinates & properties** (200000 / 0, 20480 × 20480), Save, then Generate layers
- **Import the mask through the surface-mask entry under File → Import, never "Terrain".** Row colours in the Layers manager show the layer type: height data green, satellite blue, **mask orange**. A mask imported as terrain shows a green row and red/green shading in the scene view; Generate layers then has no mask and fills every tile with the first layer (grass), with no error. Don't Rebuild terrain while a mask sits in the project as height data
- Check after generating, by counting tiles per ground texture (the `P_*.rvmat` files list texture files such as `cp_dirt_ca.paa`, not the `napa_*` names):
  ```bat
  cd /d P:\Napa\data\layers
  for %t in (cp_grass cp_broadleaf cp_dirt cp_concrete) do @(<nul set /p=%t: & findstr /m /i "%t" P_*.rvmat | find /c /v "")
  ```
  All 2,209 tiles on `cp_grass` and 0 for the rest = the mask was not used. A black `M_*_lco.png` tile also means "first layer everywhere"
- Full map tiling: 47 × 47 = 2,209 tiles, 440 m segment + 72 px overlap per 512 px tile
- Importing a 20,480 px image makes Terrain Builder build its grid file ("Generating GRID v4w file"): **20–30 minutes**, looks frozen. Terrain Builder is **32-bit** and does this on one core, so Task Manager shows ~3% CPU (one core of many) and ~1 GB of memory. Leave it alone unless CPU sits at 0 for 10+ minutes
- "Data cache open failed" lines in the Console right after an import are Terrain Builder's cache for the new layer; they stop after a Save

## Known look issues (for later)

- Buildings, cars, tree shadows and solar panels are painted into the NAIP photo. Up close they show as flat smears. When real 3D buildings and trees go in, clean or blur the satellite image under them
- Surface mask is one material (grass) everywhere. Phase 3 adds vineyard, dry hillside, asphalt and so on
