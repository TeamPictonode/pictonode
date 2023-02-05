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
from gi.repository import GtkNodes

import sys
import os

# This file was written in its entirety by Parker Nelms and Stephen Foster.

#Plugin implementation

from client import *
#from httpclient import *

def N_(message): return message
def _(message): return GLib.dgettext(None, message)


def send_image_to_daemon(button, gegl):
    
    def do_send_image(gegl):
        image = save_layer_to_png(gegl)
        #http_client.send_image(image)

    x = threading.Thread(target=do_send_image, args=(gegl,))
    x.start()
    x.join()

def save_layer_to_png(gegl_buffer):
    STATIC_TARGET_DIR = os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}\\int")
    STATIC_TARGET = os.path.abspath(f"{STATIC_TARGET_DIR}\\pictonode-intermediate.png")

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

class ImgSrcNode(GtkNodes.Node):
  __gtype_name__ = 'SrcNode'


  def __init__(self, *args, **kwds) -> None:
    super().__init__(*args, **kwds)

    self.set_label("Image Source")
    self.connect("node_func_clicked",self.remove)

  def remove(self, node):
    self.destroy()

#class based on the demo class from the gtknode img.py example
class PluginWindow(object):


  def __init__(self):
    window: Gtk.Window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
    window.set_border_width(20)

    hbox: Gtk.Box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

    button: Gtk.Button = Gtk.Button(label="Add Generic Node")
    button.connect("clicked", self.add_generic)
    hbox.add(button)

    frame = Gtk.Frame.new()

    scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
    scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    frame.add(scrolled_window)

    self.node_view: GtkNodes.NodeView = GtkNodes.NodeView()
    scrolled_window.add(self.node_view)

    full_view: Gtk.Box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    full_view.pack_start(hbox, False, False, 0)
    full_view.pack_start(frame, True, True, 0)

    window.add(full_view)
    
    window.connect("destroy", self.do_quit)
    window.show_all()
    Gtk.main()

  def add_node(self,node_type: GtkNodes.Node, widget=None):
    self.node_view.add(node_type)
    self.node_view.show_all()

  def do_quit(self, widget=None, data=None):
    Gtk.main_quit()
    sys.exit(0)

  def save(self):
    self.node_view.save("node_structure.xml")

  def add_generic(self, widget=None):
    self.node_view.add(ImgSrcNode())
    self.node_view.show_all()

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

            plugin_window: PluginWindow = PluginWindow()

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