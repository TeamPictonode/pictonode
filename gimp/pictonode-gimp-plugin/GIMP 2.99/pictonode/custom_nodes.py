# This file was written by Parker Nelms and Stephen Foster.

from httpclient import *
from client import *
import window
import pickle
import sys
import threading
import os
import uuid
import ontario
import uuid

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
# implement gegl node operations using ontario backend

class ImgSrcNode(GtkNodes.Node):
    __gtype_name__ = 'SrcNode'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window

        # when a drawable is selected from the list, this is set
        self.drawable = None
        self.drawables = self.node_window.drawables
        self.filename = None
        self.buffer_id = str(uuid.uuid1())
        self.buffer = None

        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Image Source")
        self.connect("node_func_clicked", self.remove)

        self.add_file_button: Gtk.Button = Gtk.Button(label="Open Image")
        self.add_file_button.connect("clicked", self.open_file)

        # create dropdown with drawables
        self.list_store = Gtk.ListStore(str, int)
        for i, d in enumerate(self.drawables):
            self.list_store.append(["Layer ", i])
            print("Drawable: ", d)

        self.drawable_combobox = Gtk.ComboBox.new_with_model_and_entry(self.list_store)
        self.drawable_combobox.connect("changed", self.change_layer)

        # add gtk widgets to node widget
        self.item_add(self.drawable_combobox, GtkNodes.NodeSocketIO.DISABLE)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(1.0)
        self.node_socket_output = self.item_add(
            label, GtkNodes.NodeSocketIO.SOURCE)
        self.node_socket_output.connect(
            "socket_connect", self.node_socket_connect)

    def change_layer(self, combo):
        iter = combo.get_active_iter()
        if iter is not None:
            model = combo.get_model()
            id = model[iter][1]
            self.drawable = self.drawables[id]
            self.buffer = self.drawable.get_buffer()

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
            self.filename = fn
            self.update_output()

        # close the window on "cancel"
        dialog.destroy()

    def remove(self, node):
        self.destroy()

    def process(self):
        if self.buffer:
            print("Buffer: ", self.buffer)
            self.node_window.buffer_map[self.buffer_id] = [self.buffer, self.drawable]
            return True

        return False

    def update_output(self):
        did_process = self.process()
        if did_process:
            self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def node_socket_connect(self, sink, source):
        self.update_output()


class OutputNode(GtkNodes.Node):
    __gtype_name__ = 'OutNode'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window
        # build an image contexts
        # add nodes to it
        self.incoming_buffer_id = None
        self.incoming_buffer = None

        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Output Node")
        self.connect("node_func_clicked", self.remove)

        self.save_file_button: Gtk.Button = Gtk.Button(label="Save Image")
        self.save_file_button.connect("clicked", self.save_file)

        self.item_add(self.save_file_button, GtkNodes.NodeSocketIO.DISABLE)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming)

    def save_file(self, widget=None):
        dialog = Gtk.FileChooserDialog(
            "Select An Image",
            None,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE,
             Gtk.ResponseType.OK))

        response = dialog.run()

        fn = None

        if response == Gtk.ResponseType.OK:
            fn = dialog.get_filename()
            dialog.destroy()
            print(fn)
            self.filename = fn
            self.process()

        # close the window on "cancel"
        dialog.destroy()

    def remove(self, node):
        self.destroy()

    def process(self):
        print(self.incoming_buffer)
        print(self.filename)
        print(self.node_window)
        if self.incoming_buffer and self.filename:
            print("Saving... ", self.incoming_buffer)
            # use ontario backend for image processing
            self.image_builder.load_from_buffer(self.incoming_buffer)
            self.image_builder.save_to_file(self.filename)
            self.image_builder.process()

        return False

    def node_socket_incoming(self, socket, payload):
        self.incoming_buffer_id = payload.decode('utf-8')
        print("Buffer ID incoming: ", self.incoming_buffer_id)
        self.incoming_buffer = self.node_window.buffer_map.get(
            self.incoming_buffer_id)[0]
        print("Incoming: ", self.incoming_buffer)
