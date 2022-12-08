@echo off
set GIMP_VERSION=2.99
xcopy /S /Y /F "%~dp0..\..\tests\gegl_buffer_test.py" "C:\Program Files\GIMP %GIMP_VERSION%\bin"
PAUSE