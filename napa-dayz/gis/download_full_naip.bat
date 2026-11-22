@echo off
:: Napa DayZ map: download the 2022 NAIP aerial photo tiles for the full map (Phase 2)
:: 24 GeoTIFFs (4-band RGB + near-infrared, 60 cm), about 10 GB, into D:\NapaMap\gis\raw\full_naip\
:: Source: Microsoft Planetary Computer open-data mirror of USDA NAIP (public domain).
:: Uses curl (built into Windows 10/11). Safe to re-run: finished files are skipped, partial ones resume.

setlocal
set OUT=D:\NapaMap\gis\raw\full_naip
if not exist "%OUT%" mkdir "%OUT%"
cd /d "%OUT%"

echo [1/24] m_3812237_se_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812237_se_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812237_se_10_060_20220523.tif"
echo [2/24] m_3812237_sw_10_060_20220524.tif
curl -L --fail --retry 3 -C - -o "m_3812237_sw_10_060_20220524.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812237_sw_10_060_20220524.tif"
echo [3/24] m_3812238_se_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812238_se_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812238_se_10_060_20220523.tif"
echo [4/24] m_3812238_sw_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812238_sw_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812238_sw_10_060_20220523.tif"
echo [5/24] m_3812239_se_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812239_se_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812239_se_10_060_20220523.tif"
echo [6/24] m_3812239_sw_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812239_sw_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812239_sw_10_060_20220523.tif"
echo [7/24] m_3812245_ne_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812245_ne_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812245_ne_10_060_20220523.tif"
echo [8/24] m_3812245_nw_10_060_20220524.tif
curl -L --fail --retry 3 -C - -o "m_3812245_nw_10_060_20220524.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812245_nw_10_060_20220524.tif"
echo [9/24] m_3812245_se_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812245_se_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812245_se_10_060_20220523.tif"
echo [10/24] m_3812245_sw_10_060_20220524.tif
curl -L --fail --retry 3 -C - -o "m_3812245_sw_10_060_20220524.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812245_sw_10_060_20220524.tif"
echo [11/24] m_3812246_ne_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812246_ne_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812246_ne_10_060_20220523.tif"
echo [12/24] m_3812246_nw_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812246_nw_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812246_nw_10_060_20220523.tif"
echo [13/24] m_3812246_se_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812246_se_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812246_se_10_060_20220523.tif"
echo [14/24] m_3812246_sw_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812246_sw_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812246_sw_10_060_20220523.tif"
echo [15/24] m_3812247_ne_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812247_ne_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812247_ne_10_060_20220523.tif"
echo [16/24] m_3812247_nw_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812247_nw_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812247_nw_10_060_20220523.tif"
echo [17/24] m_3812247_se_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812247_se_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812247_se_10_060_20220523.tif"
echo [18/24] m_3812247_sw_10_060_20220523.tif
curl -L --fail --retry 3 -C - -o "m_3812247_sw_10_060_20220523.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812247_sw_10_060_20220523.tif"
echo [19/24] m_3812253_ne_10_060_20220518.tif
curl -L --fail --retry 3 -C - -o "m_3812253_ne_10_060_20220518.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812253_ne_10_060_20220518.tif"
echo [20/24] m_3812253_nw_10_060_20220518.tif
curl -L --fail --retry 3 -C - -o "m_3812253_nw_10_060_20220518.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812253_nw_10_060_20220518.tif"
echo [21/24] m_3812254_ne_10_060_20220518.tif
curl -L --fail --retry 3 -C - -o "m_3812254_ne_10_060_20220518.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812254_ne_10_060_20220518.tif"
echo [22/24] m_3812254_nw_10_060_20220518.tif
curl -L --fail --retry 3 -C - -o "m_3812254_nw_10_060_20220518.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812254_nw_10_060_20220518.tif"
echo [23/24] m_3812255_ne_10_060_20220518.tif
curl -L --fail --retry 3 -C - -o "m_3812255_ne_10_060_20220518.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812255_ne_10_060_20220518.tif"
echo [24/24] m_3812255_nw_10_060_20220518.tif
curl -L --fail --retry 3 -C - -o "m_3812255_nw_10_060_20220518.tif" "https://naipeuwest.blob.core.windows.net/naip/v002/ca/2022/ca_060cm_2022/38122/m_3812255_nw_10_060_20220518.tif"

echo.
echo Done. Files in %OUT%:
dir /b *.tif | find /c ".tif"
endlocal
