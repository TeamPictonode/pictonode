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
        self.layer = None
        self.layers = self.node_window.layers
        self.filename = None
        self.buffer_id = str(uuid.uuid1())
        self.buffer = None

        # initialize our image context for the gegl nodes
        self.image_context = None
        self.image_builder = None

        self.set_label("Image Source")
        self.connect("node_func_clicked", self.remove)

        # create dropdown with layers
        self.list_store = Gtk.ListStore(str, int)
        self.list_store.append(["Select a Layer", -1])
        for i, d in enumerate(self.layers):
            self.list_store.append(["Layer: " + d.get_name(), i])
            print("Layer: ", d)

        self.layer_combobox = Gtk.ComboBox.new_with_model_and_entry(self.list_store)
        self.layer_combobox.set_entry_text_column(0)
        self.layer_combobox.set_active(0)

        # add gtk widgets to node widget
        self.item_add(self.layer_combobox, GtkNodes.NodeSocketIO.DISABLE)
        self.layer_combobox.connect("changed", self.change_layer)

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
            self.layer = self.layers[id]
            self.buffer = self.layer.get_buffer()

        did_process = self.process()
        if did_process:
            self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def remove(self, node):
        self.destroy()

    def process(self):
        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)
        if self.buffer:
            print("Buffer: ", self.buffer)
            self.node_window.buffer_map[self.buffer_id] = [self.buffer,
                                                           self.layer]
            return True

        return False

    def node_socket_connect(self, sink, source):
        did_process = self.process()
        if did_process:
            self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))


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


class InvertNode(GtkNodes.Node):
    __gtype_name__ = 'InvertNode'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window
        self.buffer_id = str(uuid.uuid1())
        self.buffer = None
        self.layer = None

        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Image Invert")
        self.connect("node_func_clicked", self.remove)

        # create node input socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming)

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
            self.layer = self.layers[id]
            self.buffer = self.layer.get_buffer()
            self.node_socket_connect()

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

    def process_input(self):
        if self.incoming_buffer:
            # use ontario backend for image processing
            self.image_builder.load_from_buffer(self.incoming_buffer)
            self.image_builder.invert()
            self.image_builder.save_to_buffer(self.incoming_buffer)
            self.image_builder.process()
            self.buffer = self.incoming_buffer

        return False

    def process_ouput(self):
        if self.buffer:
            print("Buffer: ", self.buffer)
            self.node_window.buffer_map[self.buffer_id] = [self.buffer,
                                                           self.layer]
            return True
        return False

    def value_update(self):


    def node_socket_connect(self, sink, source):
        did_process = self.process_ouput()
        if did_process:
            self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def node_socket_incoming(self, socket, payload):
        self.image_context.reset_context()
        self.incoming_buffer_id = payload.decode('utf-8')
        print("Buffer ID incoming: ", self.incoming_buffer_id)

        self.incoming_buffer = self.node_window.buffer_map.get(
            self.incoming_buffer_id)[0]

        self.layer = self.node_window.buffer_map.get(
            self.incoming_buffer_id)[1]

        print("Incoming: ", self.incoming_buffer)

        self.process_input()
