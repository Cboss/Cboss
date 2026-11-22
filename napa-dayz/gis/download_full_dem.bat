@echo off
:: Napa DayZ map: download the USGS 1 m height tiles for the full map (Phase 2)
:: 46 files, about 11 GB, into D:\NapaMap\gis\raw\full_dem\
:: Uses curl (built into Windows 10/11). Safe to re-run: finished files are skipped, partial ones resume.
::
:: The area is covered by several lidar surveys. Newer surveys only cover parts of each 10 km tile,
:: so all of them are downloaded and layered: dem_list.txt lists them oldest first, newest last,
:: and gdalbuildvrt puts the last-listed on top, with older surveys filling the gaps.

setlocal
set OUT=D:\NapaMap\gis\raw\full_dem
if not exist "%OUT%" mkdir "%OUT%"
cd /d "%OUT%"

:: --- 2017 Sacramento ---
echo x57y423  2017 Sacramento  (200 MB)
curl -L --fail --retry 3 -C - -o "USGS_one_meter_x57y423_CA_Sacramento_2017.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_Sacramento_2017/TIFF/USGS_one_meter_x57y423_CA_Sacramento_2017.tif"
echo x57y424  2017 Sacramento  (15 MB)
curl -L --fail --retry 3 -C - -o "USGS_one_meter_x57y424_CA_Sacramento_2017.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_Sacramento_2017/TIFF/USGS_one_meter_x57y424_CA_Sacramento_2017.tif"
:: --- 2018 NoCal Wildfires B5b ---
echo x54y423  2018 NoCal Wildfires B5b  (39 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x54y423_CA_NoCal_Wildfires_B5b_QL1_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCal_Wildfires_B5b_QL1_2018/TIFF/USGS_1m_x54y423_CA_NoCal_Wildfires_B5b_QL1_2018.tif"
echo x54y425  2018 NoCal Wildfires B5b  (90 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x54y425_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x54y425_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x54y426  2018 NoCal Wildfires B5b  (301 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x54y426_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x54y426_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x55y423  2018 NoCal Wildfires B5b  (213 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x55y423_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x55y423_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x55y424  2018 NoCal Wildfires B5b  (294 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x55y424_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x55y424_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x55y425  2018 NoCal Wildfires B5b  (381 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x55y425_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x55y425_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x55y426  2018 NoCal Wildfires B5b  (373 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x55y426_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x55y426_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x56y423  2018 NoCal Wildfires B5b  (339 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x56y423_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x56y423_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x56y424  2018 NoCal Wildfires B5b  (397 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x56y424_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x56y424_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x56y425  2018 NoCal Wildfires B5b  (385 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x56y425_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x56y425_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x56y426  2018 NoCal Wildfires B5b  (350 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x56y426_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x56y426_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x57y423  2018 NoCal Wildfires B5b  (280 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x57y423_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x57y423_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x57y424  2018 NoCal Wildfires B5b  (388 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x57y424_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x57y424_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x57y425  2018 NoCal Wildfires B5b  (369 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x57y425_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x57y425_CA_NoCAL_Wildfires_B5b_2018.tif"
echo x57y426  2018 NoCal Wildfires B5b  (364 MB)
curl -L --fail --retry 3 -C - -o "USGS_1m_x57y426_CA_NoCAL_Wildfires_B5b_2018.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NoCAL_Wildfires_B5b_2018/TIFF/USGS_1m_x57y426_CA_NoCAL_Wildfires_B5b_2018.tif"
:: --- 2022 Northern CA B22 ---
echo x54y423  2022 Northern CA B22  (406 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x54y423_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x54y423_CA_NorthernCA_B22.tif"
echo x54y424  2022 Northern CA B22  (397 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x54y424_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x54y424_CA_NorthernCA_B22.tif"
echo x54y425  2022 Northern CA B22  (342 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x54y425_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x54y425_CA_NorthernCA_B22.tif"
echo x54y426  2022 Northern CA B22  (151 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x54y426_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x54y426_CA_NorthernCA_B22.tif"
echo x55y423  2022 Northern CA B22  (250 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y423_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x55y423_CA_NorthernCA_B22.tif"
echo x55y424  2022 Northern CA B22  (170 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y424_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x55y424_CA_NorthernCA_B22.tif"
echo x55y425  2022 Northern CA B22  (33 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y425_CA_NorthernCA_B22.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthernCA_B22/TIFF/USGS_1M_10_x55y425_CA_NorthernCA_B22.tif"
:: --- 2023 Solano County A23 ---
echo x55y423  2023 Solano County A23  (59 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y423_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x55y423_CA_SolanoCounty_A23.tif"
echo x56y423  2023 Solano County A23  (135 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y423_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x56y423_CA_SolanoCounty_A23.tif"
echo x56y424  2023 Solano County A23  (17 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y424_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x56y424_CA_SolanoCounty_A23.tif"
echo x56y425  2023 Solano County A23  (6 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y425_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x56y425_CA_SolanoCounty_A23.tif"
echo x57y423  2023 Solano County A23  (370 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y423_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x57y423_CA_SolanoCounty_A23.tif"
echo x57y424  2023 Solano County A23  (386 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y424_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x57y424_CA_SolanoCounty_A23.tif"
echo x57y425  2023 Solano County A23  (55 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y425_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x57y425_CA_SolanoCounty_A23.tif"
echo x57y426  2023 Solano County A23  (114 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y426_CA_SolanoCounty_A23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_SolanoCounty_A23/TIFF/USGS_1M_10_x57y426_CA_SolanoCounty_A23.tif"
:: --- 2023 North Coast Ranges B23 ---
echo x54y425  2023 North Coast Ranges B23  (46 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x54y425_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x54y425_CA_NorthCoastRanges_B23.tif"
echo x54y426  2023 North Coast Ranges B23  (239 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x54y426_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x54y426_CA_NorthCoastRanges_B23.tif"
echo x55y423  2023 North Coast Ranges B23  (77 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y423_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x55y423_CA_NorthCoastRanges_B23.tif"
echo x55y424  2023 North Coast Ranges B23  (249 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y424_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x55y424_CA_NorthCoastRanges_B23.tif"
echo x55y425  2023 North Coast Ranges B23  (365 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y425_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x55y425_CA_NorthCoastRanges_B23.tif"
echo x55y426  2023 North Coast Ranges B23  (373 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x55y426_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x55y426_CA_NorthCoastRanges_B23.tif"
echo x56y423  2023 North Coast Ranges B23  (220 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y423_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x56y423_CA_NorthCoastRanges_B23.tif"
echo x56y424  2023 North Coast Ranges B23  (392 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y424_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x56y424_CA_NorthCoastRanges_B23.tif"
echo x56y425  2023 North Coast Ranges B23  (389 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y425_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x56y425_CA_NorthCoastRanges_B23.tif"
echo x56y426  2023 North Coast Ranges B23  (356 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x56y426_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x56y426_CA_NorthCoastRanges_B23.tif"
echo x57y423  2023 North Coast Ranges B23  (8 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y423_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x57y423_CA_NorthCoastRanges_B23.tif"
echo x57y424  2023 North Coast Ranges B23  (15 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y424_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x57y424_CA_NorthCoastRanges_B23.tif"
echo x57y425  2023 North Coast Ranges B23  (330 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y425_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x57y425_CA_NorthCoastRanges_B23.tif"
echo x57y426  2023 North Coast Ranges B23  (267 MB)
curl -L --fail --retry 3 -C - -o "USGS_1M_10_x57y426_CA_NorthCoastRanges_B23.tif" "https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/CA_NorthCoastRanges_B23/TIFF/USGS_1M_10_x57y426_CA_NorthCoastRanges_B23.tif"

:: Layer order for gdalbuildvrt (oldest first, newest last = on top)
if exist dem_list.txt del dem_list.txt
echo %OUT%\USGS_one_meter_x57y423_CA_Sacramento_2017.tif>> dem_list.txt
echo %OUT%\USGS_one_meter_x57y424_CA_Sacramento_2017.tif>> dem_list.txt
echo %OUT%\USGS_1m_x54y423_CA_NoCal_Wildfires_B5b_QL1_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x54y425_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x54y426_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x55y423_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x55y424_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x55y425_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x55y426_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x56y423_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x56y424_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x56y425_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x56y426_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x57y423_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x57y424_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x57y425_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1m_x57y426_CA_NoCAL_Wildfires_B5b_2018.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x54y423_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x54y424_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x54y425_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x54y426_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y423_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y424_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y425_CA_NorthernCA_B22.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y423_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y423_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y424_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y425_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y423_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y424_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y425_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y426_CA_SolanoCounty_A23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x54y425_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x54y426_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y423_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y424_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y425_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x55y426_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y423_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y424_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y425_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x56y426_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y423_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y424_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y425_CA_NorthCoastRanges_B23.tif>> dem_list.txt
echo %OUT%\USGS_1M_10_x57y426_CA_NorthCoastRanges_B23.tif>> dem_list.txt

echo.
echo Done. Files in %OUT%:
dir /b *.tif | find /c ".tif"
endlocal
