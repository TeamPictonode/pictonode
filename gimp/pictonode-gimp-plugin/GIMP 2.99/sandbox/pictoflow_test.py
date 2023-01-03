
import sys
import os

if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('Gegl', '0.4')
from gi.repository import Gegl

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi

from pictoflow import node_view


class Demo():
    def __init__(self):
        w = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        w.set_border_width(10)
        w.set_default_size(500,500)
        w.set_title("Pictoflow Demo")
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        b = Gtk.Button(label="Save")
        b.connect("clicked", self.save)
        hbox.add(b)

        b = Gtk.Button(label="Load")
        b.connect("clicked", self.load)
        hbox.add(b)

        frame = Gtk.Frame.new()

        sw = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        frame.add(sw)

        self.node_view = node_view.NodeView()
        sw.add(self.node_view)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(frame, True, True, 0)
        w.add(vbox)

        w.connect("destroy", Gtk.main_quit)
        w.show_all()
        Gtk.main()

    def save(self, widget=None):
        print("save")

    def load(self, widget=None):
        print("load")

def main():
    print("hello from sandbox!")
    Demo()

if __name__=='__main__':
    main()