'''
Written by Parker Nelms
'''

import os

# autopep8 off
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf  # noqa
# autopep on


class AboutDialog(Gtk.AboutDialog):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_authors(["Parker Nelms",
                          "Stephen Foster",
                          "Grace Meredith",
                          "John Nunley"])

        self.set_comments("Pictonode is a node-based image editor that implements the GEGL image processing library. This version is meant to be a plugin for GIMP.")
        self.set_license_type(Gtk.License.AGPL_3_0)
        self.set_program_name("Pictonode")

        # logo_path = os.path.abspath("assets/pictonode_logo.png")

        logo = GdkPixbuf.Pixbuf.new_from_file(os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/assets/pictonode_logo.png"))
        self.set_logo(logo)
