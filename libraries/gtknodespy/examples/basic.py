# GNU AGPL v3 License
# Written by John Nunley

"""
A basic demo of gtknodespy
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GObject

from gtknodes import PiNodeView

import sys

class Application(Gtk.Application):
  window: Gtk.ApplicationWindow | None

  def __init__(self, *args, **kwargs):
    super().__init__(
      *args,
      application_id="com.github.notgull.gtknodespy.basic",
      **kwargs
    )

    self.window = None

  def do_activate(self):
    window = Gtk.ApplicationWindow(application=self)
    window.set_title("gtknodespy basic demo")

    # Create a frame for decoration.
    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.IN)
    frame.set_border_width(10)
    window.add(frame)

    window.set_size_request(400, 400)
    window.show_all() 
    self.window = window

def main() -> None:
  app = Application()
  app.run(sys.argv)

if __name__ == "__main__":
  main()
