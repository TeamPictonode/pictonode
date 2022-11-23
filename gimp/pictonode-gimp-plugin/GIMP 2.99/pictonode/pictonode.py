#!/usr/bin/env python3

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
import sys

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

def entry_point(procedure, run_mode, image, n_drawables, drawables, args, data):
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class Pictonode (Gimp.PlugIn):
    ## Parameters ##
    __gproperties__ = {}

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return True, 'gimp30-python', None

    def do_query_procedures(self):
        return [ 'pictonode' ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            entry_point, None)
        procedure.set_image_types("RGB*, GRAY*");
        procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE |
                                        Gimp.ProcedureSensitivityMask.DRAWABLES)
        procedure.set_documentation (_("Pictonode"),
                                     _("Launches Pictonode plugin"),
                                     name)
        procedure.set_menu_label(_("Launch"))
        procedure.set_attribution("Stephen Foster",
                                  "Team Picto",
                                  "2022")
        procedure.add_menu_path ("<Image>/Pictonode")

        procedure.add_argument_from_property(self, "name")
        return procedure

Gimp.main(Pictonode.__gtype__, sys.argv)