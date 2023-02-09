#!/usr/bin/env python3

# This file was written in its entirety by Parker Nelms and Stephen Foster.

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
# autopep8 on


def N_(message): return message
def _(message): return GLib.dgettext(None, message)


def send_image_to_daemon(button, gegl):

    def do_send_image(gegl):
        image = save_layer_to_png(gegl)
        http_client.send_image(image)

    x = threading.Thread(target=do_send_image, args=(gegl,))
    x.start()
    x.join()


def save_layer_to_png(gegl_buffer):
    STATIC_TARGET_DIR = os.path.abspath(
        f"{os.path.dirname(os.path.abspath(__file__))}\\int")
    STATIC_TARGET = os.path.abspath(
        f"{STATIC_TARGET_DIR}\\pictonode-intermediate.png")

    # make the empty target
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


class Pictonode (Gimp.PlugIn):

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return ['pictonode']

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)
        procedure.set_image_types("RGB*, GRAY*")
        procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE |
                                       Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_documentation(_("Pictonode"),
                                    _("Launches Pictonode plugin"),
                                    name)
        procedure.set_menu_label(_("Launch"))
        procedure.set_attribution("Stephen Foster, Parker Nelms",
                                  "Team Picto",
                                  "2022")
        procedure.add_menu_path("<Image>/Pictonode")

        procedure.add_argument_from_property(self, "name")

        return procedure

    def run(
            self,
            procedure,
            run_mode,
            image,
            n_drawables,
            drawables,
            args,
            run_data):

        node_view = GtkNodes.NodeView()

        if n_drawables != 1:
            msg = _("Procedure '{}' only works with one drawable.").format(
                procedure.get_name())
            error = GLib.Error.new_literal(Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, error)
        else:
            drawable = drawables[0]

        if run_mode == Gimp.RunMode.INTERACTIVE:
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk

            GimpUi.init("pictonode.py")

            dialog = GimpUi.Dialog(use_header_bar=True,
                                   title=_("Pictonode"),
                                   role="es1-Python3")


            win = Gtk.ApplicationWindow()
            win.set_title("Pictonode")
            win.set_default_size(400, 400)

            main_window = window.PluginWindow()

            while (True):
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    position = Gimp.get_pdb().run_procedure(
                        'gimp-image-get-item-position', [image, drawable]).index(1)

                    # close dialog
                    dialog.destroy()
                    break
                else:
                    dialog.destroy()
                    return procedure.new_return_values(
                        Gimp.PDBStatusType.CANCEL, GLib.Error())

        return procedure.new_return_values(
            Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(Pictonode.__gtype__, sys.argv)
