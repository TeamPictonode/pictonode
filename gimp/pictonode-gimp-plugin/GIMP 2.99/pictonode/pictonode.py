#!/usr/bin/env python3

# This file was written in its entirety by Parker Nelms and Stephen Foster.
import os
import sys

from manager import PictonodeManager

# autopep8 off
import gi

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp  # noqa

gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi  # noqa

gi.require_version("GLib", "2.0")
from gi.repository import GLib  # noqa
# autopep8 on

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

def register_instance_parasite() -> None:
    from utils import get_pid_timestamp
    inst = f"{os.getpid()}.{get_pid_timestamp(Gimp.getpid())}"
    parasite = Gimp.Parasite.new(
        "pictonode-instance",
        Gimp.PARASITE_PERSISTENT,
        inst.encode('utf-8'))
    Gimp.attach_parasite(parasite)

def invalidate_instance_parasite() -> None:
    Gimp.detach_parasite("pictonode-instance")

def recycle_instance_parasite() -> None:
    invalidate_instance_parasite()
    register_instance_parasite()

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
                                       Gimp.ProcedureSensitivityMask.DRAWABLES |
                                       Gimp.ProcedureSensitivityMask.NO_DRAWABLES)

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

        if run_mode == Gimp.RunMode.NONINTERACTIVE or run_mode == Gimp.RunMode.WITH_LAST_VALS:
            msg = _("Procedure '{}' only works in INTERACTIVE mode!").format(
                procedure.get_name())
            error = GLib.Error.new_literal(Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(
                Gimp.PDBStatusType.CALLING_ERROR, error)

        elif run_mode == Gimp.RunMode.INTERACTIVE:
            parasite = Gimp.get_parasite("pictonode-instance")

            if parasite is None:
                register_instance_parasite()

            else:
                from utils import pid_exists, get_ppid, get_pid_timestamp

                pdata = bytes(
                    parasite.get_data()).decode("utf-8").split(".")

                suspect, timestamp = pdata[0], pdata[1]

                if pid_exists(int(suspect)):

                    # There's a chance that the registered process id is this
                    # process id, even though this process isn't who registered
                    # that instance in the parasite, or the registered process
                    # id that exists isn't associated with GIMP

                    if ((int(os.getpid()) == int(suspect)) or (
                            (int(Gimp.getpid()) != int(get_ppid(suspect))))):

                        # There's one deeper edge case where the suspect is a
                        # persistent process launched by GIMP. This is highly
                        # unlikely due to GIMP procedure nature, however it
                        # could still happen. In this scenario restarting GIMP
                        # would be sufficient. A solution could be to also
                        # register GIMPS pid in the parasite to check for this,
                        # however the flatpak version of GIMP would prove an
                        # issue for this as it runs in its own pid namespace
                        # (its pid will always be 2)

                        # *Solved* by comparing the timestamps of the GIMP process,
                        # Essentially, the registered timestamp will always be
                        # different as the only way into this scenario is when
                        # we are talking about two seperate occurrences of GIMP
                        # initiated at different times. The next elif takes
                        # care of this.

                        recycle_instance_parasite()

                    elif ((int(Gimp.getpid()) == int(get_ppid(suspect))) and (
                            get_pid_timestamp(get_ppid(suspect)) != timestamp)):

                        recycle_instance_parasite()

                    else:
                        msg = _("Procedure '{}' is already running!").format(
                            procedure.get_name())
                        msg += "\nInitiated at: " + get_pid_timestamp(int(suspect))
                        error = GLib.Error.new_literal(
                            Gimp.PlugIn.error_quark(), msg, 0)
                        return procedure.new_return_values(
                            Gimp.PDBStatusType.CALLING_ERROR, error)
                else:
                    recycle_instance_parasite()

            PictonodeManager().init(procedure, run_mode, image,
                                    n_drawables, drawables, args, run_data)

            GimpUi.init("pictonode.py")
            PictonodeManager().run()

            invalidate_instance_parasite()

        else:
            msg = _("Procedure '{}' only works in INTERACTIVE mode!").format(procedure.get_name())
            msg += "\nCall mode: " + str(run_mode)
            error = GLib.Error.new_literal(
                    Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(
                    Gimp.PDBStatusType.CALLING_ERROR, error)
        
        return procedure.new_return_values(
            Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(Pictonode.__gtype__, sys.argv)