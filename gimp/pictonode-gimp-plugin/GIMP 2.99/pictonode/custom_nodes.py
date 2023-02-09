# This file was written by Parker Nelms and Stephen Foster.

from httpclient import *
from client import *
import window

import sys
import threading
import os

# autopep8 off
import gi
gi.require_version("GIRepository", "2.0")
from gi.repository import GIRepository  # noqa

GIRepository.Repository.prepend_search_path(
    os.path.realpath(
        os.path.dirname(
            os.path.abspath(__file__)) +
        "/introspection"))

GIRepository.Repository.prepend_library_path(
    os.path.realpath(
        os.path.dirname(
            os.path.abspath(__file__)) +
        "/libs"))

gi.require_version("GtkNodes", "0.1")
from gi.repository import GtkNodes  # noqa

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp  # noqa

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi  # noqa

gi.require_version('Gegl', '0.4')
from gi.repository import Gegl  # noqa

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa

gi.require_version("GLib", "2.0")
from gi.repository import GLib  # noqa

gi.require_version("GObject", "2.0")
from gi.repository import GObject  # noqa

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf  # noqa
# autopep8 on

# node classes based on examples from img.py in the gtknodes project

# First, define different node types using GtkNodes.Node as a base type


class ImgSrcNode(GtkNodes.Node):
    __gtype_name__ = 'SrcNode'

    def __init__(self, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.filename = None

        self.set_label("Image Source")
        self.connect("node_func_clicked", self.remove)

        self.canvas: Gtk.DrawingArea = Gtk.DrawingArea()
        self.canvas.connect("draw", self.draw_image)

        self.add_file_button: Gtk.Button = Gtk.Button(label="Open Image")
        self.add_file_button.connect("clicked", self.open_file)

        self.item_add(self.add_file_button, GtkNodes.NodeSocketIO.DISABLE)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(1.0)
        self.node_socket_output = self.item_add(
            label, GtkNodes.NodeSocketIO.SOURCE)
        self.node_socket_output.connect(
            "socket_connect", self.node_socket_connect)

    def open_file(self, widget=None):
        dialog = Gtk.FileChooserDialog(
            "Select An Image",
            None,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN,
             Gtk.ResponseType.OK))

        response = dialog.run()

        fn = None

        if response == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            dialog.destroy()
            print(fn)
            self.draw_image(fn)
            self.filename = fn
            self.update_output()

        # close the window on "cancel"
        dialog.destroy()

    # information on how to make this comes from
    def draw_image(self, image_file):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_file)

    def remove(self, node):
        self.destroy()

    def update_output(self):
        self.node_socket_output.write(bytes(self.filename, 'utf8'))

    def node_socket_connect(self, sink, source):
        self.node_socket_output.write(bytes(self.filename, 'utf8'))


class OutputNode(GtkNodes.Node):
    __gtype_name__ = 'OutNode'

    def __init__(self, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.set_label("Image Output")
        self.connect("node_func_clicked", self.remove)

        # create node input socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming)

    def remove(self, node):
        self.destroy()

    def node_socket_incoming(self, socket, payload):
        self.image = payload
        print("Payload: ", payload.decode('utf8'))
        


class NumGen(GtkNodes.Node):
    __gtype_name__ = 'NumNode'

    def __init__(self, *args, **kwds) -> None:
        super().__init__(*args, **kwds)
        