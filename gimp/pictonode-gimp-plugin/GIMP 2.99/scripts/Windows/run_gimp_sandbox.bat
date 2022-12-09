@echo off
set GIMP_VERSION=2.99
set GIMP_PYTHON="C:\Program Files\GIMP %GIMP_VERSION%\bin\python3.exe"

REM %1 == first command-line argument
set SANDBOX_SCRIPT=%1

REM Execute the sandbox with CLAs 2 through 9 (skip name of script)
%GIMP_PYTHON% "%~dp0..\..\sandbox\%SANDBOX_SCRIPT%" %2 %3 %4 %5 %6 %7 %8 %9
PAUSE