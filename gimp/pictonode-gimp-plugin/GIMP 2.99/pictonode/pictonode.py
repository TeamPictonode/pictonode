#!/usr/bin/env python3

# This file was written in its entirety by Parker Nelms and Stephen Foster.

from httpclient import *
from client import *
from manager import PictonodeManager
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
            msg = _("Procedure '{}' only works in INTERACTIVE mode.").format(
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
                        msg += "\nInitiated at: " + timestamp
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
            raise Exception(">:(")
        print(get_pid_timestamp(Gimp.getpid()))
        return procedure.new_return_values(
            Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(Pictonode.__gtype__, sys.argv)