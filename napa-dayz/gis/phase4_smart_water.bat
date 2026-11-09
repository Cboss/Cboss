@echo off
:: Napa DayZ map: Phase 4a "smart water" heights
:: Run from the OSGeo4W Shell. Needs the Phase 3 OSM download (raw\osm\water.osm).
::
:: Keeps the Napa River, sloughs and low ponds as water (at least 2 m deep) and lifts the
:: rest of the flooded marsh to dry, walkable flats just above the waterline.
:: Replaces P:\Napa\source\napa_dem.asc (the old one is kept as napa_dem_phase2.asc).

setlocal
set GIS=D:\NapaMap\gis
set P=P:\Napa
set RAW=https://raw.githubusercontent.com/Cboss/Cboss/ccr-3b451e26-3japm5/napa-dayz

cd /d "%GIS%"
curl -sSL --fail -o "%GIS%\napa_smart_water.py" %RAW%/gis/napa_smart_water.py || goto :fail
python "%GIS%\napa_smart_water.py" || goto :fail

if not exist "%P%\source\napa_dem_phase2.asc" (
  copy /y "%P%\source\napa_dem.asc" "%P%\source\napa_dem_phase2.asc" >nul
  copy /y "%P%\source\napa_dem.prj" "%P%\source\napa_dem_phase2.prj" >nul
  echo   kept the old height map as source\napa_dem_phase2.asc
)
copy /y "%GIS%\full\napa_dem_water.asc" "%P%\source\napa_dem.asc" >nul && echo   source\napa_dem.asc updated
copy /y "%GIS%\full\napa_dem_water.prj" "%P%\source\napa_dem.prj" >nul

echo.
echo Done. Look at %GIS%\full\water_preview.png (blue = water, yellow = marsh lifted to dry land)
endlocal
exit /b 0

:fail
echo Stopped: the step above failed.
endlocal
exit /b 1
