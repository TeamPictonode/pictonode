@echo off
set GIMP_VERSION=2.99
xcopy /S /Y /F "%~dp0..\..\pictonode" "C:\Users\%username%\AppData\Roaming\GIMP\%GIMP_VERSION%\plug-ins\pictonode"
PAUSE