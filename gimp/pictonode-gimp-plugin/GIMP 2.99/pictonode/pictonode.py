#!/usr/bin/env python3
import threading
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

#Plugin impl
from client import *

def N_(message): return message
def _(message): return GLib.dgettext(None, message)


def send_message_to_controller_callback(button, msg):
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
            win.set_default_size(1000, 500)

            grid = Gtk.Grid()

            image_display = Gtk.Image()
            image_path = image.get_file().get_path()
            image_display.set_from_file(image_path)


            '''
                Sending an image to controller works like this:
                
                START
                    -Plugin sends init message to controller (Hey dude im sending an image in a sec and its a png/svg/whatever)
                    -Plugin waits for controller to confirm (Controller replies saying thats chill bro)
                    -Plugin sends image chunks then waits for controller to confirm (Controller replies mmm yummy)
                END
            '''

            button = Gtk.Button(label="Send To Controller")
            button.connect('clicked', send_image_to_controller_callback, drawable.get_buffer())

            grid.attach(button, 0, 2, 20, 10)
            grid.attach(image_display, 0, 1, 1000, 500)

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
        
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(Pictonode.__gtype__, sys.argv)