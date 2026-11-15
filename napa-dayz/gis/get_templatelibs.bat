@echo off
:: Napa DayZ map: download Bohemia's Terrain Builder template libraries (Phase 4b)
:: From the official DayZ terrain sample (BohemiaInteractive/DayZ-Samples, Test_Terrain),
:: licence ADPL-SA (attribution, non-commercial, share alike; DayZ/Arma only).
:: Saves 14 .tml files to P:\Napa\source\TemplateLibs\

setlocal
set OUT=P:\Napa\source\TemplateLibs
set SRC=https://raw.githubusercontent.com/BohemiaInteractive/DayZ-Samples/master/Test_Terrain/source/TemplateLibs
if not exist "%OUT%" mkdir "%OUT%"
for %%L in (roads water plantsnew residential industrial military specific walls signs rocks ruins wrecks rail test) do (
  curl -sSL --fail -o "%OUT%\%%L.tml" %SRC%/%%L.tml && echo   %%L.tml
)
echo.
echo Done. In Terrain Builder: Library manager - right-click Template libraries - load/import each .tml from %OUT%
endlocal
