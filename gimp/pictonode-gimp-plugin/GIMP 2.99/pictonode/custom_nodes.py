# This file was written by Parker Nelms and Stephen Foster.

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

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi  # noqa

gi.require_version("GtkNodes", "0.1")
from gi.repository import GtkNodes  # noqa

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf  # noqa
# autopep8 on

# node classes based on examples from img.py in the gtknodes project

# First, define generic custom node type using GtkNodes.Node as a base type
# implement gegl node operations using ontario backend


class CustomNode(GtkNodes.Node):

    def __init__(self, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.set_can_focus(True)
        self.connect("node_func_clicked", self.remove)

    def set_values(self, values: dict):
        '''Virtual Method to be overriden by custom nodes'''
        pass

    def remove(self, node):
        dialog = Gtk.Dialog(title="Are you sure?", parent=None, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dialog.set_default_size(75, 50)

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            self.destroy()

    def get_values(self):
        return {}


class ImgSrcNode(CustomNode):
    __gtype_name__ = 'ImgSrc'

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


class OutputNode(CustomNode):
    __gtype_name__ = 'ImgOut'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window

        # lock output node
        if self.node_window:
            self.node_window.output_node_lock(True)

        # build an image contexts
        # add nodes to it
        self.incoming_buffer_id = None
        self.incoming_buffer = None

        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Output Node")

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
        # have to override output remove to deal with button lock and display update

        # create confirmation dialog box first
        dialog = Gtk.Dialog(title="Are you sure?",
                            parent=None, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dialog.set_default_size(75, 50)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            dialog.destroy()
            # unlock output node
            self.node_window.output_node_lock(False)

            # delete display image
            if os.path.exists("/tmp/gimp/temp.png"):
                os.remove("/tmp/gimp/temp.png")
                self.node_window.display_output()

            self.destroy()

        dialog.destroy()

    def update_display(self):
        if self.incoming_buffer:
            # update image displayed
            self.image_builder.load_from_buffer(self.incoming_buffer)
            self.image_builder.save_to_file("/tmp/gimp/temp.png")
            self.image_builder.process()

            self.node_window.display_output()
            self.image_context.reset_context()
        else:
            # delete image displayed
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


class InvertNode(CustomNode):
    __gtype_name__ = 'Invert'

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


class CompositeNode(CustomNode):
    __gtype_name__ = 'CompOver'

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
        self.x: float = 0.0
        self.y: float = 0.0
        self.scale: float = 1.0

        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder1 = ontario.ImageBuilder(self.image_context)
        self.image_builder2 = ontario.ImageBuilder(self.image_context)

        self.set_label("Image Composite")

        # add argument fields
        self.label1 = Gtk.Label(label="X translate")
        self.label2 = Gtk.Label(label="Y translate")
        self.label3 = Gtk.Label(label="Scale")

        self.entry1 = Gtk.Entry()
        self.entry2 = Gtk.Entry()
        self.entry3 = Gtk.Entry()

        self.entry1.set_text(str(self.x))
        self.entry2.set_text(str(self.y))
        self.entry3.set_text(str(self.scale))

        self.entry1.connect("activate", self.entry_change, 1)
        self.entry2.connect("activate", self.entry_change, 2)
        self.entry3.connect("activate", self.entry_change, 3)

        self.item_add(self.label1, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.entry1, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.label2, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.entry2, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.label3, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.entry3, GtkNodes.NodeSocketIO.DISABLE)

        # create node input sockets

        # input socket 1
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming, 1)
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect, 1)

        # input socket 2
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(0.0)
        self.node_socket_input = self.item_add(
            label, GtkNodes.NodeSocketIO.SINK)
        self.node_socket_input.connect(
            "socket_incoming", self.node_socket_incoming, 2)
        self.node_socket_input.connect(
            "socket_disconnect", self.node_socket_disconnect, 2)

        # create node output socket
        label: Gtk.Label = Gtk.Label.new("Image")
        label.set_xalign(1.0)
        self.node_socket_output = self.item_add(
            label, GtkNodes.NodeSocketIO.SOURCE)
        self.node_socket_output.connect(
            "socket_connect", self.node_socket_connect)

    def get_values(self):

        ''' Returns dictionary of current state of custom values for the node '''

        custom_values = {"x": self.x,
                         "y": self.y,
                         "scale": self.scale}

        return custom_values

    def set_values(self, values: dict):

        ''' Sets custom node defaults from dictionary '''
        self.x = values.get('x')
        self.y = values.get('y')
        self.scale = values.get('scale')

        # set entry text for each entry box
        self.entry1.set_text(str(self.x))
        self.entry2.set_text(str(self.y))
        self.entry3.set_text(str(self.scale))

    def process_input(self):
        if self.incoming_buffer1 and self.incoming_buffer2:

            print("Icoming 1: ", self.incoming_buffer1)
            print("Icoming 2: ", self.incoming_buffer2)

            self.buffer = self.incoming_buffer1.dup()
            # use ontario backend for image processing
            self.image_builder1.load_from_buffer(self.incoming_buffer1)
            self.image_builder2.load_from_buffer(self.incoming_buffer2)
            self.image_builder2.translate(self.x, self.y)

            width = int(self.scale * self.buffer.get_property("width"))
            height = int(self.scale * self.buffer.get_property("height"))

            print("Width: ", width)
            print("Height: ", height)

            self.image_builder2.resize(width, height)
            self.image_builder1.composite(self.image_builder2)
            self.image_builder1.save_to_buffer(self.buffer)
            self.image_builder1.process()
            print("Comp output: ", self.buffer)

        # update buffer saved in map and resend reference
        self.value_update()

    def entry_change(self, entry, entry_id):
        '''
        Checks entry input, updates values, and processes buffer
        '''

        self.grab_focus()

        if entry_id == 1:
            # let sanitize our inputs
            try:
                value = float(entry.get_text())
                entry.set_text(str(value))
                if value < -1000000:
                    entry.set_text("-1000000.0")
                    value = -1000000.0
                elif value > 1000000:
                    entry.set_text("1000000.0")
                    value = 1000000.0
            except ValueError:
                entry.set_text("0.0")
                value = 0.0

            self.x = value

        elif entry_id == 2:
            # let sanitize our inputs
            try:
                value = float(entry.get_text())
                entry.set_text(str(value))
                if value < -1000000:
                    entry.set_text("-1000000.0")
                    value = -1000000.0
                elif value > 1000000:
                    entry.set_text("1000000.0")
                    value = 1000000.0
            except ValueError:
                entry.set_text("0.0")
                value = 0.0

            self.y = value

        elif entry_id == 3:
            # let sanitize our inputs
            try:
                value = float(entry.get_text())
                entry.set_text(str(value))
                if value < -9000.0:
                    entry.set_text("-9000.0")
                    value = -9000.0
                elif value > 9000.0:
                    entry.set_text("9000.0")
                    value = 9000.0
            except ValueError:
                entry.set_text("100.0")
                value = 100.0

            self.scale = value

        self.process_input()

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


class BlurNode(CustomNode):
    __gtype_name__ = 'GaussBlur'

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

        # add argument fields
        self.xlabel = Gtk.Label(label="std-dev-x")
        self.ylabel = Gtk.Label(label="std-dev-y")

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

    def get_values(self):

        ''' Returns dictionary of current state of custom values for the node '''

        custom_values = {"std_dev_x": self.std_dev_x,
                         "std_dev_y": self.std_dev_y}

        return custom_values

    def set_values(self, values: dict):

        ''' Sets custom node defaults from dictionary '''
        self.std_dev_x = values.get('std_dev_x')
        self.std_dev_y = values.get('std_dev_y')

        # set entry text for each entry box
        self.xentry.set_text(str(self.std_dev_x))
        self.yentry.set_text(str(self.std_dev_y))

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

        self.grab_focus()

        # let sanitize our inputs
        try:
            value = float(entry.get_text())
            entry.set_text(str(value))
            if value < 0:
                entry.set_text("0.0")
                value = 0.0
            elif value > 100:
                entry.set_text("100.0")
                value = 100.0
        except ValueError:
            entry.set_text("0.0")
            value = 0.0

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


class BrightContNode(CustomNode):
    __gtype_name__ = 'BrightCont'

    def __init__(self, node_window, *args, **kwds) -> None:
        super().__init__(*args, **kwds)

        self.node_window = node_window
        self.buffer_id = str(uuid.uuid1())
        self.buffer = None
        self.layer = None

        # default operation arguments
        self.brightness: float = 0.0
        self.contrast: float = 1.0

        # initialize our image context for the gegl nodes
        self.image_context = ontario.ImageContext()
        self.image_builder = ontario.ImageBuilder(self.image_context)

        self.set_label("Bright/Contrast")

        # add argument fields
        self.label1 = Gtk.Label(label="Brightness")
        self.label2 = Gtk.Label(label="Contrast")

        self.entry1 = Gtk.Entry()
        self.entry2 = Gtk.Entry()

        self.entry1.set_text(str(self.brightness))
        self.entry2.set_text(str(self.contrast))

        self.entry1.connect("activate", self.entry_change, 1)
        self.entry2.connect("activate", self.entry_change, 2)

        self.item_add(self.label1, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.entry1, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.label2, GtkNodes.NodeSocketIO.DISABLE)
        self.item_add(self.entry2, GtkNodes.NodeSocketIO.DISABLE)

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

    def get_values(self):

        ''' Returns dictionary of current state of custom values for the node '''

        custom_values = {"brightness": self.brightness,
                         "contrast": self.contrast}

        return custom_values

    def set_values(self, values: dict):

        ''' Sets custom node defaults from dictionary '''
        self.brightness = values.get('brightness')
        self.contrast = values.get('contrast')

        # set entry text for each entry box
        self.entry1.set_text(str(self.brightness))
        self.entry2.set_text(str(self.contrast))

    def process_input(self):
        if self.incoming_buffer:
            # set internal copy of buffer
            self.buffer = self.incoming_buffer.dup()

            # use ontario backend for image processing
            self.image_builder.load_from_buffer(self.buffer)
            self.image_builder.brightness_contrast(self.brightness, self.contrast)
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
        Checks entry input, updates values, and processes buffer
        '''

        self.grab_focus()

        if entry_id == 1:
            # let sanitize our inputs
            try:
                value = float(entry.get_text())
                entry.set_text(str(value))
                if value < -1:
                    entry.set_text("-1.0")
                    value = -1.0
                elif value > 1.0:
                    entry.set_text("1.0")
                    value = 1.0
            except ValueError:
                entry.set_text("0.0")
                value = 0.0

            self.brightness = value

        elif entry_id == 2:
             # let sanitize our inputs
            try:
                value = float(entry.get_text())
                entry.set_text(str(value))
                if value < 0:
                    entry.set_text("0.0")
                    value = 0.0
                elif value > 2.0:
                    entry.set_text("2.0")
                    value = 2.0
            except ValueError:
                entry.set_text("1.0")
                value = 1.0

            self.contrast = value

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
