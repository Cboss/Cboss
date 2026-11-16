@echo off
:: Napa test patch: start DayZ (diagnostic exe) offline on the NapaPilot map.
:: Edit the three paths below if yours differ.

set DAYZ=D:\Steam\steamapps\common\DayZ
set MOD=D:\NapaMap\@NapaPilot
set MISSION=%DAYZ%\Missions\dayzOffline.NapaPilot

start "" "%DAYZ%\DayZDiag_x64.exe" "-mod=%MOD%" "-mission=%MISSION%" -nosplash -noPause -noBenchmark -doLogs
