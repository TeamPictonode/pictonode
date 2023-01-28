import os
import sys
import gi

if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

def print_giapi(api, recursive=False):
    apiname = api.__name__.replace("gi.repository.", "")
    filename = f"{apiname}_{api._version}"
    outfile = os.path.realpath(os.path.dirname(os.path.abspath(__file__))+ "/apis/" + filename)
    with open(outfile, "w") as file:
        version_header = f"{filename}\n{api.__name__}\n\n"
        file.write(version_header)
        for l in dir(api):
            file.write(l + '\n')

def main():
    giimported = list(filter((lambda f: ("gi.repository.") in f), sys.modules))
    for giapi in giimported:
        print_giapi(sys.modules[giapi])

if __name__=="__main__":
    main()