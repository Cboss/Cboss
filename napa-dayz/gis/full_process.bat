@echo off
:: Napa DayZ map: FULL map processing (Phase 2)
:: Run from the OSGeo4W Shell (installed with QGIS).
:: Expects downloads in D:\NapaMap\gis\raw\full_dem\ (USGS 1 m DEM tiles)
::                 and D:\NapaMap\gis\raw\full_naip\ (NAIP 2024 tiles, .tif or .jp2)
::
:: Real-world area: X 547000-570040, Y 4228000-4251040 (EPSG:26910), 23,040 m square
:: In-game: 20,480 m, 4096 grid x 5 m cells, 8/9 scale
:: Satellite: 20,480 x 20,480 px (1 m per in-game pixel)
::
:: Takes a while (the satellite image is 20,480 px square). Needs ~40 GB free.

setlocal
cd /d D:\NapaMap\gis
if not exist full mkdir full

set EXTENT=547000 4228000 570040 4251040
set WARPOPTS=-overwrite -multi -wo NUM_THREADS=ALL_CPUS -wm 2048

:: ================= Height map =================
echo.
echo === Height map: 4096 x 4096, heights x 8/9 ===
:: dem_list.txt (written by download_full_dem.bat) layers the lidar surveys oldest first, newest on top
gdalbuildvrt -overwrite -input_file_list raw\full_dem\dem_list.txt full\dem_src.vrt
:: -r average: each 5.6 m cell gets the mean of the ~30 lidar points inside it (smoother than cubic when shrinking 1 m data)
gdalwarp %WARPOPTS% -te %EXTENT% -ts 4096 4096 -r average -ot Float32 full\dem_src.vrt full\full_dem.tif
call gdal_calc -A full\full_dem.tif --outfile=full\full_dem_s.tif --calc="A*0.8889" --overwrite

:: Check for gaps: STATISTICS_MINIMUM must not be -999999 (or another huge negative)
gdalinfo -stats full\full_dem_s.tif | findstr /i "STATISTICS_MINIMUM STATISTICS_MAXIMUM"

:: Terrain Builder height map: origin 200000/0, 5 m cells, labelled UTM 31N to match the project zone
gdal_translate -of AAIGrid -a_srs EPSG:32631 -a_ullr 200000 20480 220480 0 full\full_dem_s.tif full\napa_dem.asc

:: World Machine copy: 16-bit PNG, -10 m .. 1000 m mapped to 0 .. 65535
:: (in-game height = pixel / 65535 * 1010 - 10)
gdal_translate -ot UInt16 -scale -10 1000 0 65535 -of PNG full\full_dem_s.tif full\napa_dem_wm16.png

:: ================= Satellite image =================
echo.
echo === Satellite: 20480 x 20480 px ===
:: -srcnodata: ignore the black edges on NAIP tiles so they don't cover the neighbouring tile
if exist raw\full_naip\*.tif (
  gdalbuildvrt -overwrite -srcnodata "0 0 0 0" full\naip_src.vrt raw\full_naip\*.tif
) else (
  gdalbuildvrt -overwrite -srcnodata "0 0 0 0" full\naip_src.vrt raw\full_naip\*.jp2
)
gdalwarp %WARPOPTS% -te %EXTENT% -ts 20480 20480 -r average -co BIGTIFF=YES -co TILED=YES -co COMPRESS=DEFLATE full\naip_src.vrt full\full_naip.tif

:: Look for black holes (missing tiles) in this preview before going further
gdal_translate -a_nodata none -b 1 -b 2 -b 3 -outsize 2048 2048 -of PNG full\full_naip.tif full\preview_sat_2048.png

gdal_translate -a_nodata none -b 1 -b 2 -b 3 -of PNG -co ZLEVEL=3 full\full_naip.tif full\napa_sat.png
:: Near-infrared band, for painting vegetation in the surface mask
gdal_translate -a_nodata none -b 4 -of PNG -co ZLEVEL=3 full\full_naip.tif full\napa_nir.png

echo.
echo Done. Check full\preview_sat_2048.png for gaps, then copy to P:\Napa\source:
echo   full\napa_dem.asc  full\napa_dem.prj  full\napa_sat.png  full\napa_nir.png
endlocal
