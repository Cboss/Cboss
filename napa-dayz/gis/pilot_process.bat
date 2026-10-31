@echo off
:: Napa DayZ map: test patch processing
:: Run from the OSGeo4W Shell (installed with QGIS).
:: Expects downloads in raw\dem\ (USGS 1 m DEM) and raw\naip\ (NAIP photos).
:: Real-world area: X 555430-558310, Y 4232870-4235750 (EPSG:26910), 2,880 m.
:: In-game: 2,560 m, 512 grid x 5 m, 8/9 scale.

cd /d D:\NapaMap\gis

:: --- Height map: 512 x 512, heights scaled to 8/9 ---
gdalbuildvrt -overwrite dem_src.vrt raw\dem\*.tif
gdalwarp -overwrite -te 555430 4232870 558310 4235750 -ts 512 512 -r cubic -ot Float32 dem_src.vrt pilot_dem.tif
:: If gdal_calc is not found, use gdal_calc.py
call gdal_calc -A pilot_dem.tif --outfile=pilot_dem_s.tif --calc="A*0.8889" --overwrite
:: Put it at Terrain Builder's origin (Easting 200000, Northing 0) with 5 m cells
gdal_translate -of AAIGrid -a_ullr 200000 2560 202560 0 pilot_dem_s.tif pilot_dem.asc

:: --- Satellite image: 2560 x 2560 px = 1 m per pixel ---
:: If NAIP came as .jp2 files, change *.tif to *.jp2
:: -srcnodata: ignore the black edges on NAIP tiles so they don't cover the neighbouring tile
gdalbuildvrt -overwrite -srcnodata "0 0 0 0" naip_src.vrt raw\naip\*.tif
gdalwarp -overwrite -te 555430 4232870 558310 4235750 -ts 2560 2560 -r cubic naip_src.vrt pilot_naip.tif
gdal_translate -b 1 -b 2 -b 3 -of PNG pilot_naip.tif pilot_sat.png
:: Near-infrared band: plants show up bright, useful for painting vineyards and oaks
gdal_translate -b 4 -of PNG pilot_naip.tif pilot_nir.png

echo.
echo Done. Copy pilot_dem.asc and pilot_sat.png to P:\NapaPilot\source
