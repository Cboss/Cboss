@echo off
:: Napa DayZ map: set up P:\Napa for the full-map Terrain Builder project (Phase 2)
:: Run from the OSGeo4W Shell AFTER full_process.bat.
:: Creates the folders, copies the processed height map and images, makes a starter
:: all-grass surface mask and legend, copies the grass material, and writes layers.cfg.

setlocal
set GIS=D:\NapaMap\gis\full
set P=P:\Napa

if not exist "%GIS%\napa_dem.asc" (
  echo Can't find %GIS%\napa_dem.asc - run full_process.bat first.
  exit /b 1
)

echo === Folders ===
for %%D in (source data world) do if not exist "%P%\%%D" mkdir "%P%\%%D"

echo === Height map and images ===
copy /y "%GIS%\napa_dem.asc" "%P%\source\" >nul
copy /y "%GIS%\napa_dem.prj" "%P%\source\" >nul
copy /y "%GIS%\napa_sat.png" "%P%\source\" >nul
copy /y "%GIS%\napa_nir.png" "%P%\source\" >nul

echo === Starter surface mask (all grass) and legend ===
gdal_create -of GTiff -outsize 20480 20480 -bands 3 -burn 0 -burn 255 -burn 0 -ot Byte -co COMPRESS=DEFLATE "%GIS%\napa_mask.tif"
gdal_translate -q -of PNG "%GIS%\napa_mask.tif" "%P%\source\napa_mask.png"
gdal_create -of GTiff -outsize 64 64 -bands 3 -burn 0 -burn 255 -burn 0 -ot Byte "%GIS%\legend.tif"
gdal_translate -q -of PNG "%GIS%\legend.tif" "%P%\source\mapLegend.png"

echo === Grass material ===
copy /y "P:\DZ\surfaces\data\terrain\cp_grass.rvmat" "%P%\data\napa_grass.rvmat" >nul

echo === layers.cfg ===
(
echo // Napa full map: surface layers for Terrain Builder. Starter: one surface ^(grass^).
echo class Layers
echo {
echo 	class napa_grass
echo 	{
echo 		texture = "";
echo 		material = "Napa\data\napa_grass.rvmat";
echo 	};
echo };
echo.
echo class Legend
echo {
echo 	picture = "Napa\source\mapLegend.png";
echo 	class Colors
echo 	{
echo 		napa_grass[] = {{0,255,0}};
echo 	};
echo };
) > "%P%\source\layers.cfg"

echo.
echo Done. Contents of %P%\source:
dir /b "%P%\source"
echo.
dir /b "%P%\data"
endlocal
