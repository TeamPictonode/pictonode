'''
    This is a sandbox template

    Feel free to copy this template to make new scripts to play around with these typelibs and for example try out
    GEGL examples.

    Windows CLI usage:
        .\scripts\Windows\run_gimp_sandbox.bat <name of sandbox script> <any CLAs go here>

        Running this script (gimp_sandbox.py) would then be:
            .\scripts\Windows\run_gimp_sandbox.bat gimp_sandbox.py
'''

# Import Gimp's GObject typelibs by setting an environment variable GI_TYPELIB_PATH
# We can use any typelib dependency found in "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

import sys
import os

if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

import gi

gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi


# Put anything you want to test with gimp's python dependencies here :)
def main():
    print("hello from sandbox!")

if __name__=='__main__':
    main()