@echo off
:: Napa DayZ map: Phase 3 surfaces (ground types and grass)
:: Run from the OSGeo4W Shell (its Python has GDAL and numpy).
::
::   1. Gets the latest surface script, layers.cfg and config.cpp from the repo
::   2. Downloads OpenStreetMap roads, land use, water and buildings for the map area
::   3. Builds the 20,480 px surface mask from the photo + OSM + height map
::   4. Puts the mask, layers.cfg, config.cpp and the four ground materials into P:\Napa
::
:: Safe to re-run: finished OSM downloads are kept.

setlocal
set GIS=D:\NapaMap\gis
set OSM=%GIS%\raw\osm
set P=P:\Napa
set RAW=https://raw.githubusercontent.com/Cboss/Cboss/ccr-3b451e26-3japm5/napa-dayz
set BOX=(38.190,-122.470,38.416,-122.190)

if not exist "%OSM%" mkdir "%OSM%"
cd /d "%GIS%"

echo.
echo === 1. Latest files from the repo ===
curl -sSL --fail -o "%GIS%\napa_surface_mask.py" %RAW%/gis/napa_surface_mask.py || goto :fail
echo   napa_surface_mask.py

echo.
echo === 2. OpenStreetMap (can take a few minutes) ===
echo [out:xml][timeout:600];(way["highway"]%BOX%;);(._;^>;);out body;> "%OSM%\q_roads.txt"
echo [out:xml][timeout:600];(way["landuse"]%BOX%;relation["landuse"]%BOX%;way["amenity"="parking"]%BOX%;way["aeroway"]%BOX%;);(._;^>;);out body;> "%OSM%\q_landuse.txt"
echo [out:xml][timeout:600];(way["natural"="water"]%BOX%;relation["natural"="water"]%BOX%;way["waterway"~"river|canal"]%BOX%;);(._;^>;);out body;> "%OSM%\q_water.txt"
echo [out:xml][timeout:600];(way["building"]%BOX%;);(._;^>;);out body;> "%OSM%\q_buildings.txt"
call :get roads
call :get landuse
call :get water
call :get buildings

echo.
echo === 3. Surface mask (20,480 px, about 10-20 minutes) ===
python "%GIS%\napa_surface_mask.py" || goto :fail

echo.
echo === 4. Into P:\Napa ===
copy /y "%GIS%\full\napa_mask.png" "%P%\source\napa_mask.png" >nul && echo   source\napa_mask.png
curl -sSL --fail -o "%P%\source\layers.cfg" %RAW%/terrain/napa/layers.cfg && echo   source\layers.cfg
curl -sSL --fail -o "%P%\config.cpp" %RAW%/terrain/napa/config.cpp && echo   config.cpp
copy /y "P:\DZ\surfaces\data\terrain\cp_grass.rvmat"             "%P%\data\napa_grass.rvmat"    >nul && echo   data\napa_grass.rvmat
copy /y "P:\DZ\surfaces\data\terrain\cp_broadleaf_sparse1.rvmat" "%P%\data\napa_forest.rvmat"   >nul && echo   data\napa_forest.rvmat
copy /y "P:\DZ\surfaces\data\terrain\cp_dirt.rvmat"              "%P%\data\napa_dirt.rvmat"     >nul && echo   data\napa_dirt.rvmat
copy /y "P:\DZ\surfaces\data\terrain\cp_concrete1.rvmat"         "%P%\data\napa_concrete.rvmat" >nul && echo   data\napa_concrete.rvmat

echo.
echo Done. Look at %GIS%\full\napa_mask_preview.png before going into Terrain Builder.
endlocal
exit /b 0

:get
findstr /c:"</osm>" "%OSM%\%~1.osm" >nul 2>&1 && (echo   %~1.osm already downloaded& exit /b 0)
for %%H in (overpass-api.de overpass.kumi.systems overpass.private.coffee) do (
  echo   %~1 from %%H ...
  curl -sS -m 900 --data-urlencode "data@%OSM%\q_%~1.txt" -o "%OSM%\%~1.osm" https://%%H/api/interpreter
  findstr /c:"</osm>" "%OSM%\%~1.osm" >nul 2>&1 && (echo   %~1.osm OK& exit /b 0)
)
echo   %~1.osm FAILED - the mask is built without it. Run this script again later to retry.
exit /b 1

:fail
echo.
echo Stopped: the step above failed.
endlocal
exit /b 1
