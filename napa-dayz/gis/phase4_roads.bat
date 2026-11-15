@echo off
:: Napa DayZ map: Phase 4c roads - graded road bed + highway road parts
:: Run from the OSGeo4W Shell (its Python has GDAL and numpy).
::
::   1. Gets the latest scripts, part tables and the road guide from the repo
::   2. Grades a smooth bed under every road in the height map (napa_road_bed.py)
::   3. Lays the highway and ramp road parts on that bed (napa_road_objects.py)
::   4. Puts the new height map and the object list into the Napa project folder
::
:: The old height map is kept as source\napa_dem_phase4a.asc.

setlocal
set GIS=D:\NapaMap\gis
set RAW=https://raw.githubusercontent.com/Cboss/Cboss/ccr-3b451e26-3japm5/napa-dayz
set P=D:\DayZ Projects\Napa
if not exist "%P%\source" set P=P:\Napa
if not exist "%P%\source" ( echo Napa project folder not found. & exit /b 1 )
if not exist "%GIS%\full\full_dem_water.tif" ( echo %GIS%\full\full_dem_water.tif not found - run phase4_smart_water.bat first. & exit /b 1 )

if not exist "%GIS%\roadgen" mkdir "%GIS%\roadgen"
if not exist "%GIS%\full\roads_guide" mkdir "%GIS%\full\roads_guide"
if not exist "%P%\source\roads" mkdir "%P%\source\roads"
cd /d "%GIS%"

echo.
echo === 1. Latest files from the repo ===
curl -sSL --fail -o "%GIS%\napa_road_bed.py" %RAW%/gis/napa_road_bed.py || goto :fail
curl -sSL --fail -o "%GIS%\napa_road_objects.py" %RAW%/gis/napa_road_objects.py || goto :fail
for %%F in (asf1 asf2 asf3 city grav mud) do (
  curl -sSL --fail -o "%GIS%\roadgen\road_parts_%%F.csv" %RAW%/gis/roadgen/road_parts_%%F.csv || goto :fail
)
for %%E in (shp shx dbf prj cpg) do (
  curl -sSL --fail -o "%GIS%\full\roads_guide\napa_roads_guide.%%E" %RAW%/terrain/napa/roads_guide/napa_roads_guide.%%E || goto :fail
)
echo   scripts, part tables and road guide OK

echo.
echo === 2. Road bed (about a minute) ===
python "%GIS%\napa_road_bed.py" || goto :fail

echo.
echo === 3. Highway and ramp parts (about a minute) ===
python "%GIS%\napa_road_objects.py" --family asf1 --dem "%GIS%\full\full_dem_roads.tif" --out "%GIS%\full\roads_asf1.txt" || goto :fail
python "%GIS%\napa_road_objects.py" --family asf3 --highway motorway_link trunk_link primary_link secondary_link tertiary_link --dem "%GIS%\full\full_dem_roads.tif" --out "%GIS%\full\roads_ramps.txt" || goto :fail
copy /b /y "%GIS%\full\roads_asf1.txt"+"%GIS%\full\roads_ramps.txt" "%GIS%\full\napa_roads_highways.txt" >nul

echo.
echo === 4. Into %P%\source ===
if not exist "%P%\source\napa_dem_phase4a.asc" (
  copy /y "%P%\source\napa_dem.asc" "%P%\source\napa_dem_phase4a.asc" >nul
  copy /y "%P%\source\napa_dem.prj" "%P%\source\napa_dem_phase4a.prj" >nul
  echo   kept the old height map as source\napa_dem_phase4a.asc
)
copy /y "%GIS%\full\napa_dem_roads.asc" "%P%\source\napa_dem.asc" >nul && echo   source\napa_dem.asc updated
copy /y "%GIS%\full\napa_dem_roads.prj" "%P%\source\napa_dem.prj" >nul
copy /y "%GIS%\full\napa_roads_highways.txt" "%P%\source\roads\napa_roads_highways.txt" >nul && echo   source\roads\napa_roads_highways.txt updated

echo.
echo Done. Next in Terrain Builder: refresh napa_dem.asc, Rebuild terrain, re-import the road objects.
endlocal
exit /b 0

:fail
echo.
echo Stopped: the step above failed.
endlocal
exit /b 1
