@echo off
:: Napa DayZ map: Phase 4c roads - main roads and two-lane roads
:: Run from the OSGeo4W Shell, after phase4_roads.bat (needs its graded height map).
::
:: Lays the asf2 parts (primary / secondary: Silverado Trail, Soscol, Imola, Trancas, Jefferson)
:: and the asf3 parts (tertiary / unclassified two-lane roads) on the road bed and puts the
:: object list into the Napa project folder as source\roads\napa_roads_main.txt.
:: No terrain change: the bed under these roads was graded by phase4_roads.bat.

setlocal
set GIS=D:\NapaMap\gis
:: Optional first argument: a commit id to fetch the files from (default: the branch)
set REF=ccr-3b451e26-3japm5
if not "%~1"=="" set REF=%~1
set RAW=https://raw.githubusercontent.com/Cboss/Cboss/%REF%/napa-dayz
set P=D:\DayZ Projects\Napa
if not exist "%P%\source" set P=P:\Napa
if not exist "%P%\source" ( echo Napa project folder not found. & exit /b 1 )
if not exist "%GIS%\full\full_dem_roads.tif" ( echo %GIS%\full\full_dem_roads.tif not found - run phase4_roads.bat first. & exit /b 1 )
if not exist "%P%\source\roads" mkdir "%P%\source\roads"
cd /d "%GIS%"

echo.
echo === 1. Latest script ===
curl -sSL --fail -o "%GIS%\napa_road_objects.py" %RAW%/gis/napa_road_objects.py || goto :fail
echo   napa_road_objects.py OK

echo.
echo === 2. Main roads, asf2 (a few minutes, prints nothing while it works) ===
python "%GIS%\napa_road_objects.py" --family asf2 --highway primary secondary --dem "%GIS%\full\full_dem_roads.tif" --out "%GIS%\full\roads_asf2.txt" || goto :fail

echo.
echo === 3. Two-lane roads, asf3 (a few minutes) ===
python "%GIS%\napa_road_objects.py" --family asf3 --highway tertiary unclassified --dem "%GIS%\full\full_dem_roads.tif" --out "%GIS%\full\roads_asf3.txt" || goto :fail

copy /b /y "%GIS%\full\roads_asf2.txt"+"%GIS%\full\roads_asf3.txt" "%GIS%\full\napa_roads_main.txt" >nul
copy /y "%GIS%\full\napa_roads_main.txt" "%P%\source\roads\napa_roads_main.txt" >nul && echo   source\roads\napa_roads_main.txt updated

echo.
echo Done. In Terrain Builder: File - Import - Objects - source\roads\napa_roads_main.txt (once).
endlocal
exit /b 0

:fail
echo.
echo Stopped: the step above failed.
endlocal
exit /b 1
