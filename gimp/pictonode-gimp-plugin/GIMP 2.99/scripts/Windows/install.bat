@echo off

rem This file was written in its entirety by Parker Nelms and Stephen Foster.

set GIMP_VERSION=2.99
xcopy /S /Y /F "%~dp0..\..\pictonode" "C:\Users\%username%\AppData\Roaming\GIMP\%GIMP_VERSION%\plug-ins\pictonode"
PAUSE