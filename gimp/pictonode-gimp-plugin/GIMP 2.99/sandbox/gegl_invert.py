'''
    This is sandbox example of using GEGL to invert a JPG

    Windows CLI usage:
        .\scripts\Windows\run_gimp_sandbox.bat <name of sandbox script> <any CLAs go here>

        Running this script (gegl_invert.py) would then be:
            .\scripts\Windows\run_gimp_sandbox.bat gegl_invert.py <Complete Path to Input JPG> <Complete Path to Output JPG>
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

def do_GEGL_invert():
    try:
        #[index 1 (inclusive) to index 3 (exclusive)]
        origin, target = sys.argv[1:3]
    except IndexError:
        sys.stderr.write("Usage: %s origin_jpg target_jpg" % __file__)
        sys.exit(1)

    print(f"Inverting {origin} to {target}")

    Gegl.init([])

    ops = Gegl.list_operations()

    x = Gegl.Node()

    y = Gegl.Node()
    y.set_property("operation", "gegl:jpg-load")
    y.set_property("path", origin)
    x.add_child(y)

    z = Gegl.Node()
    z.set_property("operation", "gegl:invert")
    x.add_child(z)

    w = Gegl.Node()
    w.set_property("operation", "gegl:jpg-save")
    w.set_property("path", target)
    x.add_child(w)

    y.connect_to("output", z, "input")
    z.connect_to("output", w, "input")

    w.process()

def main():
    do_GEGL_invert()

if __name__=='__main__':
    main()