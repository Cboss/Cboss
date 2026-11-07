@echo off
:: Napa test patch: start a local DayZDiag server on the NapaPilot map, then a client that joins it.
:: Edit the paths below if yours differ.

set DAYZ=D:\Steam\steamapps\common\DayZ
set MOD=D:\NapaMap\@NapaPilot
set MISSION=%DAYZ%\Missions\dayzOffline.NapaPilot
set CFG=%~dp0serverDZ_napapilot.cfg
set SERVERPROFILE=D:\NapaMap\server_profile

if not exist "%SERVERPROFILE%" mkdir "%SERVERPROFILE%"

echo Starting local server...
start "NapaPilot server" "%DAYZ%\DayZDiag_x64.exe" -server "-config=%CFG%" "-mod=%MOD%" "-mission=%MISSION%" -port=2302 "-profiles=%SERVERPROFILE%" -doLogs -filePatching

echo Waiting 30 seconds for the server to load the map...
timeout /t 30

echo Starting client...
start "NapaPilot client" "%DAYZ%\DayZDiag_x64.exe" "-mod=%MOD%" -connect=127.0.0.1 -port=2302 -name=Boss -nosplash -noPause -doLogs -filePatching
