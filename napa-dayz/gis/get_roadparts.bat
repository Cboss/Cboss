@echo off
:: Napa DayZ map: Bohemia's updated road parts for the Terrain Builder Road Tool (Phase 4c)
:: Source: BohemiaInteractive/DayZ-Misc, "Road Parts/Chernarus" (linked from the wiki page
:: "DayZ: Using Road Tool in Terrain Builder"). 109 parts: asf1, asf2, asf3, city, grav, mud + crossroads.
:: Backs up the current parts folder to parts_backup first, then overwrites.

setlocal
set OUT=P:\DZ\structures\roads\parts
set SRC=https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Misc/master/Road%%20Parts/Chernarus
if not exist "P:\DZ" ( echo P:\DZ not found - extract the game data first. & exit /b 1 )
if exist "%OUT%" (
  if not exist "%OUT%_backup" ( xcopy /e /i /q "%OUT%" "%OUT%_backup" >nul && echo   backed up to %OUT%_backup )
) else (
  mkdir "%OUT%" && echo   created %OUT%
)
set N=0

curl -sSL --fail -o "%OUT%\asf1_0 2000.p3d" "%SRC%/asf1_0%%202000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_1 1000.p3d" "%SRC%/asf1_1%%201000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_10 100.p3d" "%SRC%/asf1_10%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_10 25.p3d" "%SRC%/asf1_10%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_10 50.p3d" "%SRC%/asf1_10%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_10 75.p3d" "%SRC%/asf1_10%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_12.p3d" "%SRC%/asf1_12.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_15 75.p3d" "%SRC%/asf1_15%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_22 50.p3d" "%SRC%/asf1_22%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_25.p3d" "%SRC%/asf1_25.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_30 25.p3d" "%SRC%/asf1_30%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_6.p3d" "%SRC%/asf1_6.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_60 10.p3d" "%SRC%/asf1_60%%2010.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_6_crosswalk.p3d" "%SRC%/asf1_6_crosswalk.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_6konec.p3d" "%SRC%/asf1_6konec.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf1_7 100.p3d" "%SRC%/asf1_7%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_0 2000.p3d" "%SRC%/asf2_0%%202000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_1 1000.p3d" "%SRC%/asf2_1%%201000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_10 100.p3d" "%SRC%/asf2_10%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_10 25.p3d" "%SRC%/asf2_10%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_10 50.p3d" "%SRC%/asf2_10%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_10 75.p3d" "%SRC%/asf2_10%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_12.p3d" "%SRC%/asf2_12.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_15 75.p3d" "%SRC%/asf2_15%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_22 50.p3d" "%SRC%/asf2_22%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_25.p3d" "%SRC%/asf2_25.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_30 25.p3d" "%SRC%/asf2_30%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_6.p3d" "%SRC%/asf2_6.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_60 10.p3d" "%SRC%/asf2_60%%2010.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_6_crosswalk.p3d" "%SRC%/asf2_6_crosswalk.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_6konec.p3d" "%SRC%/asf2_6konec.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf2_7 100.p3d" "%SRC%/asf2_7%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_0 2000.p3d" "%SRC%/asf3_0%%202000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_1 1000.p3d" "%SRC%/asf3_1%%201000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_10 100.p3d" "%SRC%/asf3_10%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_10 25.p3d" "%SRC%/asf3_10%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_10 50.p3d" "%SRC%/asf3_10%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_10 75.p3d" "%SRC%/asf3_10%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_12.p3d" "%SRC%/asf3_12.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_15 75.p3d" "%SRC%/asf3_15%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_22 50.p3d" "%SRC%/asf3_22%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_25.p3d" "%SRC%/asf3_25.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_30 25.p3d" "%SRC%/asf3_30%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_6.p3d" "%SRC%/asf3_6.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_60 10.p3d" "%SRC%/asf3_60%%2010.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_6konec.p3d" "%SRC%/asf3_6konec.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\asf3_7 100.p3d" "%SRC%/asf3_7%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_0 2000.p3d" "%SRC%/city_0%%202000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_1 1000.p3d" "%SRC%/city_1%%201000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_10 100.p3d" "%SRC%/city_10%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_10 25.p3d" "%SRC%/city_10%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_10 50.p3d" "%SRC%/city_10%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_10 75.p3d" "%SRC%/city_10%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_12.p3d" "%SRC%/city_12.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_15 75.p3d" "%SRC%/city_15%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_22 50.p3d" "%SRC%/city_22%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_25.p3d" "%SRC%/city_25.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_30 25.p3d" "%SRC%/city_30%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_6.p3d" "%SRC%/city_6.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_60 10.p3d" "%SRC%/city_60%%2010.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_6_crosswalk.p3d" "%SRC%/city_6_crosswalk.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_6konec.p3d" "%SRC%/city_6konec.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\city_7 100.p3d" "%SRC%/city_7%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_0 2000.p3d" "%SRC%/grav_0%%202000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_1 1000.p3d" "%SRC%/grav_1%%201000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_10 100.p3d" "%SRC%/grav_10%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_10 25.p3d" "%SRC%/grav_10%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_10 50.p3d" "%SRC%/grav_10%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_10 75.p3d" "%SRC%/grav_10%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_12.p3d" "%SRC%/grav_12.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_15 75.p3d" "%SRC%/grav_15%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_22 50.p3d" "%SRC%/grav_22%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_25.p3d" "%SRC%/grav_25.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_30 25.p3d" "%SRC%/grav_30%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_6.p3d" "%SRC%/grav_6.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_60 10.p3d" "%SRC%/grav_60%%2010.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_6konec.p3d" "%SRC%/grav_6konec.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\grav_7 100.p3d" "%SRC%/grav_7%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf1_asf2.p3d" "%SRC%/kr_t_asf1_asf2.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf1_asf3.p3d" "%SRC%/kr_t_asf1_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf1_city.p3d" "%SRC%/kr_t_asf1_city.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf2_asf2.p3d" "%SRC%/kr_t_asf2_asf2.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf2_asf3.p3d" "%SRC%/kr_t_asf2_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf3_asf2.p3d" "%SRC%/kr_t_asf3_asf2.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf3_asf3.p3d" "%SRC%/kr_t_asf3_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_asf3_mud.p3d" "%SRC%/kr_t_asf3_mud.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_city_asf3.p3d" "%SRC%/kr_t_city_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_city_city.p3d" "%SRC%/kr_t_city_city.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_t_mud_mud.p3d" "%SRC%/kr_t_mud_mud.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_x_asf1_asf3.p3d" "%SRC%/kr_x_asf1_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_x_asf1_city.p3d" "%SRC%/kr_x_asf1_city.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_x_asf2_asf3.p3d" "%SRC%/kr_x_asf2_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_x_city_city.p3d" "%SRC%/kr_x_city_city.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\kr_x_city_city_asf3.p3d" "%SRC%/kr_x_city_city_asf3.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_0 2000.p3d" "%SRC%/mud_0%%202000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_1 1000.p3d" "%SRC%/mud_1%%201000.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_10 100.p3d" "%SRC%/mud_10%%20100.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_10 25.p3d" "%SRC%/mud_10%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_10 50.p3d" "%SRC%/mud_10%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_10 75.p3d" "%SRC%/mud_10%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_12.p3d" "%SRC%/mud_12.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_15 75.p3d" "%SRC%/mud_15%%2075.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_22 50.p3d" "%SRC%/mud_22%%2050.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_25.p3d" "%SRC%/mud_25.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_30 25.p3d" "%SRC%/mud_30%%2025.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_6.p3d" "%SRC%/mud_6.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_60 10.p3d" "%SRC%/mud_60%%2010.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_6konec.p3d" "%SRC%/mud_6konec.p3d" && set /a N+=1 >nul
curl -sSL --fail -o "%OUT%\mud_7 100.p3d" "%SRC%/mud_7%%20100.p3d" && set /a N+=1 >nul

echo   %N% of 109 road parts downloaded to %OUT%
endlocal
