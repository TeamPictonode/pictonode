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
        self.layer_combobox.set_margin_top(20)
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
            if id >= 0:
                self.layer = self.layers[id]
                self.buffer = self.layer.get_buffer()
            else:
                self.layer = None
                self.buffer = None

        print("Image layer: ", self.layer)
        print("Image Buffer: ", self.buffer)

        self.process()
        self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def remove(self, node):
        self.destroy()

    def get_values(self):
        return {}

    def process(self):
        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        print("Buffer: ", self.buffer)
        self.node_window.buffer_map[self.buffer_id] = [self.buffer,
                                                        self.layer]

        if self.buffer:
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

        # lock output node
        self.node_window.output_node_lock(True)

        # build an image contexts
        # add nodes to it
        self.incoming_buffer_id = None
        self.incoming_buffer = None

        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Output Node")
        self.connect("node_func_clicked", self.remove)

        # initialize save file button and set it to disabled by default
        self.save_file_button: Gtk.Button = Gtk.Button(label="Save Image")
        self.save_file_button.set_margin_top(20)
        self.save_file_button.connect("clicked", self.save_file)
        self.item_add(self.save_file_button, GtkNodes.NodeSocketIO.DISABLE)
        self.save_file_button.set_sensitive(False)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming)
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect)

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
        # unlock output node
        self.node_window.output_node_lock(False)

        # delete display image
        if os.path.exists("/tmp/gimp/temp.png"):
            os.remove("/tmp/gimp/temp.png")
            self.node_window.display_output()

        self.destroy()

    def get_values(self):
        return {}

    def update_display(self):
        if self.incoming_buffer:
            # display changes
            pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB,
                                        True,
                                        8,
                                        self.incoming_buffer.props.width,
                                        self.incoming_buffer.props.height)

            self.image_builder.load_from_buffer(self.incoming_buffer)
            self.image_builder.save_to_file("/tmp/gimp/temp.png")
            self.image_builder.process()

            self.node_window.display_output()
            self.image_context.reset_context()
        else:
            os.remove("/tmp/gimp/temp.png")
            self.node_window.display_output()

    def process(self):
        if self.incoming_buffer and self.filename:
            print("Saving... ", self.incoming_buffer)
            # use ontario backend for image processing
            self.image_builder.load_from_buffer(self.incoming_buffer)
            self.image_builder.save_to_file(self.filename)
            self.image_builder.process()
            self.image_context.reset_context()

        else:
            print("could not update image, buffer not available")
        return False

    def node_socket_disconnect(self, socket, sink):
        '''
        Processes socket disconnect and updates output accordingly
        '''

        # disable save file button
        self.save_file_button.set_sensitive(False)

        # reset buffer reference information
        self.incoming_buffer_id = None
        self.incoming_buffer = None
        self.update_display()

    def node_socket_incoming(self, socket, payload):
        self.incoming_buffer_id = payload.decode('utf-8')
        print("Buffer ID incoming: ", self.incoming_buffer_id)
        self.incoming_buffer = self.node_window.buffer_map.get(
            self.incoming_buffer_id)[0]
        print("Output Incoming: ", self.incoming_buffer)
        self.update_display()

        print("Output buffer: ", self.incoming_buffer)
        # disable or enable save file button depending on
        # whether a buffer is available
        if self.incoming_buffer:
            self.save_file_button.set_sensitive(True)
        else:
            self.save_file_button.set_sensitive(False)


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
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(1.0)
        self.node_socket_output = self.item_add(
            label, GtkNodes.NodeSocketIO.SOURCE)
        self.node_socket_output.connect(
            "socket_connect", self.node_socket_connect)

    def remove(self, node):
        self.destroy()

    def get_values(self):
        return {}

    def process_input(self):
        if self.incoming_buffer:
            # set new internal copy of buffer
            self.buffer = self.incoming_buffer.dup()
            # use ontario backend for image processing
            self.image_builder.load_from_buffer(self.buffer)
            self.image_builder.invert()
            self.image_builder.save_to_buffer(self.buffer)
            self.image_builder.process()

        # update buffer saved in map and resend reference
        self.value_update()

    def process_ouput(self):
        '''
        Updates buffer reference in map
        '''

        print("Buffer: ", self.buffer)
        self.node_window.buffer_map[self.buffer_id] = [self.buffer, self.layer]

        if self.buffer:
            return True
        return False

    def value_update(self):
        '''
        Processes image and sends out updated buffer reference
        '''

        did_process = self.process_ouput()

        if not did_process:
            print("Error: could not process invert")

        self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def node_socket_disconnect(self, socket, sink):
        '''
        Processes socket disconnect and updates output accordingly
        '''

        # reset buffer reference information
        self.incoming_buffer_id = None
        self.incoming_buffer = None
        self.buffer = None
        self.layer = None
        self.process_input()

    def node_socket_connect(self, sink, source):
        '''
        Sends buffer reference upon initial socket connection
        '''

        self.value_update()

    def node_socket_incoming(self, socket, payload):
        '''
        Updates node internal state upon update from socket.
        '''

        # reset buffer reference information
        self.incoming_buffer_id = None
        self.incoming_buffer = None
        self.buffer = None
        self.layer = None

        # set new buffer information
        if payload:
            self.image_context.reset_context()
            self.incoming_buffer_id = payload.decode('utf-8')
            print("Buffer ID incoming: ", self.incoming_buffer_id)

            self.incoming_buffer = self.node_window.buffer_map.get(
                self.incoming_buffer_id)[0]

            self.layer = self.node_window.buffer_map.get(
                self.incoming_buffer_id)[1]

            print("Invert Incoming: ", self.incoming_buffer)

            self.process_input()
        else:
            print("Error!!!")


class CompositeNode(GtkNodes.Node):
    __gtype_name__ = 'CompNode'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window
        self.buffer_id = str(uuid.uuid1())

        # buffer and layers initialized for both images
        self.incoming_buffer1_id = None
        self.incoming_buffer1 = None
        self.incoming_buffer2_id = None
        self.incoming_buffer2 = None

        # initialize output buffer and layer
        self.buffer = None
        self.layer = None

        # default operation arguments
        self.opacity: float = 1
        self.x: float = 1000
        self.y: float = 100
        self.scale: float = 1

        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder1 = ontario.ImageBuilder(self.image_context)
        self.image_builder2 = ontario.ImageBuilder(self.image_context)

        self.set_label("Image Composite")
        self.connect("node_func_clicked", self.remove)

        # create node input sockets

        # input socket 1
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming, 1)
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect)

        # input socket 2
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming, 2)
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(1.0)
        self.node_socket_output = self.item_add(
            label, GtkNodes.NodeSocketIO.SOURCE)
        self.node_socket_output.connect(
            "socket_connect", self.node_socket_connect)

    def remove(self, node):
        self.destroy()

    def get_values(self):

        ''' Returns dictionary of current state of custom values for the node'''

        return {"opacity": self.opacity,
                "x": self.x,
                "y": self.y,
                "scale": self.scale}

    def process_input(self):
        if self.incoming_buffer1 and self.incoming_buffer2:

            print("Icoming 1: ", self.incoming_buffer1)
            print("Icoming 2: ", self.incoming_buffer2)

            self.buffer = self.incoming_buffer1.dup()
            # use ontario backend for image processing
            self.image_builder1.load_from_buffer(self.incoming_buffer1)
            self.image_builder1.composite(self.incoming_buffer2,
                                          self.opacity,
                                          self.x,
                                          self.y,
                                          self.scale)

            self.image_builder1.save_to_buffer(self.buffer)
            self.image_builder1.process()
            print("Comp output: ", self.buffer)

        # update buffer saved in map and resend reference
        self.value_update()

    def process_ouput(self):
        '''
        Updates buffer reference in map
        '''

        print("Buffer: ", self.buffer)
        self.node_window.buffer_map[self.buffer_id] = [self.buffer, self.layer]

        if self.buffer:
            return True
        return False

    def value_update(self):
        '''
        Processes image and sends out updated buffer reference
        '''

        did_process = self.process_ouput()

        if not did_process:
            print("Error: could not process composite")

        self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def node_socket_disconnect(self, socket, sink, datasource):
        '''
        Processes socket disconnect and updates output accordingly
        '''

        # reset buffer reference information
        if datasource == 1:
            self.incoming_buffer1_id = None
            self.incoming_buffer1 = None
        elif datasource == 2:
            self.incoming_buffer2_id = None
            self.incoming_buffer2 = None

        self.buffer = None
        self.layer = None
        self.process_input()

    def node_socket_connect(self, sink, source):
        '''
        Sends buffer reference upon initial socket connection
        '''

        self.value_update()

    def node_socket_incoming(self, socket, payload, datasource):
        '''
        Updates node internal state upon update from socket.
        '''

        # reset buffer reference based on which socket is changed
        if datasource == 1:
            self.incoming_buffer1_id = None
            self.incoming_buffer1 = None
        elif datasource == 2:
            self.incoming_buffer2_id = None
            self.incoming_buffer2 = None

        self.buffer = None
        self.layer = None

        # set new buffer information
        if payload:
            self.image_context.reset_context()
            if datasource == 1:
                self.incoming_buffer1_id = payload.decode('utf-8')
                print("Buffer ID 1 incoming: ", self.incoming_buffer1_id)
                self.incoming_buffer1 = self.node_window.buffer_map.get(
                    self.incoming_buffer1_id)[0]
            elif datasource == 2:
                self.incoming_buffer2_id = payload.decode('utf-8')
                print("Buffer ID 2 incoming: ", self.incoming_buffer2_id)
                self.incoming_buffer2 = self.node_window.buffer_map.get(
                    self.incoming_buffer2_id)[0]

            self.layer = self.node_window.buffer_map.get(
                self.incoming_buffer1_id)[1]

            print("Comp Incoming 1: ", self.incoming_buffer1)
            print("Comp Incoming 2: ", self.incoming_buffer2)

            self.process_input()
        else:
            print("Error!!!")


class BlurNode(GtkNodes.Node):
    __gtype_name__ = 'BlurNode'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window
        self.buffer_id = str(uuid.uuid1())
        self.buffer = None
        self.layer = None

        # default operation arguments
        self.std_dev_x: float = 1.5
        self.std_dev_y: float = 1.5

        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Image Blur")
        self.connect("node_func_clicked", self.remove)

        # add argument fields
        self.xlabel = Gtk.Label("std-dev-x")
        self.ylabel = Gtk.Label("std-dev-y")

        self.xentry = Gtk.Entry()
        self.yentry = Gtk.Entry()

        self.xentry.set_text(str(self.std_dev_x))
        self.yentry.set_text(str(self.std_dev_y))

        self.xentry.connect("activate", self.entry_change, 1)
        self.yentry.connect("activate", self.entry_change, 2)

        self.item_add(self.xlabel, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.xentry, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.ylabel, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.yentry, GtkNodes.NodeSocketIO.DISABLE)

        # create node input socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming)
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(1.0)
        self.node_socket_output = self.item_add(
            label, GtkNodes.NodeSocketIO.SOURCE)
        self.node_socket_output.connect(
            "socket_connect", self.node_socket_connect)

    def remove(self, node):
        self.destroy()

    def get_values(self):

        ''' Returns dictionary of current state of custom values for the node'''
        
        custom_values = {}
        custom_values["std_dev_x"] = self.std_dev_x
        custom_values["std_dev_y"] = self.std_dev_y

        return custom_values

    def process_input(self):
        if self.incoming_buffer:
            # set internal copy of buffer
            self.buffer = self.incoming_buffer.dup()

            # use ontario backend for image processing
            self.image_builder.load_from_buffer(self.buffer)
            self.image_builder.gaussian_blur(self.std_dev_x, self.std_dev_y)
            self.image_builder.save_to_buffer(self.buffer)
            self.image_builder.process()

        # update buffer saved in map and resend reference
        self.value_update()

    def process_ouput(self):
        '''
        Updates buffer reference in map
        '''

        print("Buffer: ", self.buffer)
        self.node_window.buffer_map[self.buffer_id] = [self.buffer, self.layer]

        if self.buffer:
            return True
        return False

    def entry_change(self, entry, entry_id):
        '''
        Checks entry input, update values, and processes buffer
        '''

        value = float(entry.get_text())

        # remove keyboard focus from entry box
        entry.grab_remove()

        # let sanitize our inputs
        try:
            if value < 0:
                entry.set_text("0")
            elif value > 100:
                entry.set_text("1")
        except ValueError:
            entry.set_text("0")

        # set new values
        if entry_id == 1:
            self.std_dev_x = value

        elif entry_id == 2:
            self.std_dev_y = value

        self.process_input()

    def value_update(self):
        '''
        Processes image and sends out updated buffer reference
        '''

        did_process = self.process_ouput()

        if not did_process:
            print("Error: could not process invert")

        self.node_socket_output.write(bytes(self.buffer_id, 'utf8'))

    def node_socket_disconnect(self, socket, sink):
        '''
        Processes socket disconnect and updates output accordingly
        '''

        # reset buffer reference information
        self.incoming_buffer_id = None
        self.incoming_buffer = None
        self.buffer = None
        self.layer = None
        self.process_input()

    def node_socket_connect(self, sink, source):
        '''
        Sends buffer reference upon initial socket connection
        '''

        self.value_update()

    def node_socket_incoming(self, socket, payload):
        '''
        Updates node internal state upon update from socket.
        '''

        # reset buffer reference information
        self.incoming_buffer_id = None
        self.incoming_buffer = None
        self.buffer = None
        self.layer = None

        # set new buffer information
        if payload:
            self.image_context.reset_context()
            self.incoming_buffer_id = payload.decode('utf-8')
            print("Buffer ID incoming: ", self.incoming_buffer_id)

            self.incoming_buffer = self.node_window.buffer_map.get(
                self.incoming_buffer_id)[0]

            self.layer = self.node_window.buffer_map.get(
                self.incoming_buffer_id)[1]

            print("Invert Incoming: ", self.incoming_buffer)

            self.process_input()
        else:
            print("Error!!!")
