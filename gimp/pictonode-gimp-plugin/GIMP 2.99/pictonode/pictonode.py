#!/usr/bin/env python3
import threading
import json
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import sys
import os

# This file was written in its entirety by Parker Nelms and Stephen Foster.

#Plugin impl
from client import *
from user import *

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

def deserialize(bitstream):
    """takes a bitstream and returns a deserialized json object"""
    return json.loads(bitstream)

def convert_to_file(msg):
    """convert bitstream to file"""
    f = open('./', 'wb')
    f.write(msg)
    f.close()

def send_data_to_daemon(image, node_tree):
    """sends image metadata and node objects to daemon"""
    pass

def receive_from_daemon(user: User):
    """Receives user data from daemon to update the plugin"""
    client.connect_to_controller()
    while(True):
        #wait for message
        user_data = deserialize(client.receive_user_update())
        user = User(user_data["name"],user_data["username"],user_data["last_login_date"])
        print(user.name,user.username,user.last_login_date)
        #TODO: update the ui with changes


def send_message_to_controller_callback(button, msg):

    """"""

    client.connect_to_controller()
    client.send_message_to_controller(msg)
    client.receive_message_from_controller()

    client.close_connection_to_controller()

def send_image_to_controller_callback(button, gegl):
    def do_send_image(gegl):
        client.connect_to_controller()

        image = save_layer_to_png(gegl)

        client.send_message_to_controller(f"{str(os.stat(image).st_size)}")
        client.receive_message_from_controller()

        client.send_image_to_controller(image)

    x = threading.Thread(target=do_send_image, args=(gegl,))
    x.start()
    x.join()

    client.receive_message_from_controller()
    #client.receive_image_from_controller()

    client.close_connection_to_controller()

def save_layer_to_png(gegl_buffer):
    STATIC_TARGET_DIR = f"{os.path.dirname(os.path.abspath(__file__))}\\int"
    STATIC_TARGET = f"{STATIC_TARGET_DIR}\\pictonode-intermediate.png"

    #make the empty target
    os.makedirs(STATIC_TARGET_DIR, exist_ok=True)
    intermediate_file = os.open(STATIC_TARGET, os.O_CREAT | os.O_TRUNC)
    os.close(intermediate_file)

    Gegl.init(None)
    parent = Gegl.Node()

    buffer_input = Gegl.Node()
    buffer_input.set_property("operation", "gegl:buffer-source")
    buffer_input.set_property("buffer", gegl_buffer)
    parent.add_child(buffer_input)

    buffer_output = Gegl.Node()
    buffer_output.set_property("operation", "gegl:png-save")
    buffer_output.set_property("path", STATIC_TARGET)
    parent.add_child(buffer_output)

    buffer_input.connect_to("output", buffer_output, "input")

    buffer_output.process()

    return STATIC_TARGET


def entry_point(procedure, run_mode, image, n_drawables, drawables, args, data):
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def add_op(button2, op_name, image_path):
    Gegl.init([])
    x = Gegl.Node()

    y = Gegl.Node()
    y.set_property("operation", "gegl:jpg-load")
    y.set_property("path", image_path)
    x.add_child(y)

    z = []
    z.append(Gegl.Node())
    z[0].set_property("operation", op_name)
    x.add_child(z[0])

    w = Gegl.Node()
    w.set_property("operation", "gegl:jpg-save")
    w.set_property("path", image_path)
    x.add_child(w)

    y.connect_to("output", z[0], "input")
    z[0].connect_to("output", w, "input")

    w.process()

    tree = []
    for i in x.get_children():
        tree.append([i.get_gegl_operation(),i.get_parent(),i.get_children()])

    print("Tree: ", tree)

    return tree


class Pictonode (Gimp.PlugIn):

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return [ 'pictonode' ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                        Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_documentation (_("Pictonode"),
                                     _("Launches Pictonode plugin"),
                                     name)
        procedure.set_menu_label(_("Launch"))
        procedure.set_attribution("Stephen Foster, Parker Nelms",
                                  "Team Picto",
                                  "2022")
        procedure.add_menu_path ("<Image>/Pictonode")

        procedure.add_argument_from_property(self, "name")

        return procedure

    def run(self, procedure, run_mode, image, n_drawables, drawables, args, run_data):
        if n_drawables != 1:
            msg = _("Procedure '{}' only works with one drawable.").format(procedure.get_name())
            error = GLib.Error.new_literal(Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, error)
        else:
            drawable = drawables[0]

        #create a new thread for receiving user updates from daemon
        user = None
        t1 = threading.Thread(target=receive_from_daemon, args=(user,))
        t1.start()

        if run_mode == Gimp.RunMode.INTERACTIVE:
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk

            GimpUi.init("pictonode.py")

            print(drawable.get_buffer())

            dialog = GimpUi.Dialog(use_header_bar=True,
                                   title=_("Pictonode"),
                                   role="es1-Python3")

            dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
            dialog.add_button(_("_Source"), Gtk.ResponseType.APPLY)
            dialog.add_button(_("_OK"), Gtk.ResponseType.OK)
            
            win = Gtk.ApplicationWindow()
            win.set_title("Pictonode")
            win.set_default_size(400, 400)

            grid = Gtk.Grid()

            #grabs a pixbuf of the currently selected image and displays it
            image_display = Gtk.Image()
            image_path = image.get_file().get_path()
            image_display.set_from_file(image_path)
            image_display.set_from_pixbuf(image_display.get_pixbuf())

            '''
                Sending an image to controller works like this:
                
                START
                    -Plugin sends init message to controller (Hey dude im sending an image in a sec and its a png/svg/whatever)
                    -Plugin waits for controller to confirm (Controller replies saying thats chill bro)
                    -Plugin sends image chunks then waits for controller to confirm (Controller replies mmm yummy)
                END
            '''


            button = Gtk.Button(label="Send To Controller")
            button.connect('clicked', send_image_to_controller_callback, "user_json_example.txt")

            button2 = Gtk.Button(label="Invert")
            button2.connect('clicked', add_op, "gegl:c2g", image_path)

            scrolled = Gtk.ScrolledWindow()
            scrolled.add_with_viewport(image_display)
            scrolled.set_min_content_height(500)
            scrolled.set_min_content_width(400)

            grid.attach(button, 0, 3, 2, 1)
            #grid.attach(button2, 0, 3, 2, 1)
            grid.attach(scrolled, 0, 1, 100, 2)

            win.add(grid)
            win.show_all()

            ''' geometry = Gdk.Geometry()
            geometry.min_aspect = 0.5
            geometry.max_aspect = 1.0
            dialog.set_geometry_hints(None, geometry, Gdk.WindowHints.ASPECT)
            '''

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            img = Gtk.Image.new_from_file('C:/Users/parke/Pictures/Camera Roll/example.jpg')

            frame_rgb = Gtk.Frame(label='RGB image')
            box.pack_start(frame_rgb, True, True, 0)
            
            dialog.get_content_area().add(box)
            box.show()

            while (True):

                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    position = Gimp.get_pdb().run_procedure('gimp-image-get-item-position',
                                 [image,
                                  drawable]).index(1)

                    # close dialog
                    dialog.destroy()
                    break
                else:
                    dialog.destroy()
                    return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                                       GLib.Error())
        
        t1.join()
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(Pictonode.__gtype__, sys.argv)