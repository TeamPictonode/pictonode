# GNU AGPL v3 License
# Written by John Nunley, derived from code originally written by aluntzer
# See source here: https://github.com/aluntzer/gtknodes

"""
A full implementation of a node graph in GTK.
"""

from enum import Enum

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GObject

class Action(Enum):
  NONE = 0
  DRAG_CHILD = 1
  DRAG_NODE = 2
  RESIZE = 3

class PiNodeView(Gtk.Container):
  """
  A node graph view.
  """

  __gtype_name__: str = "PiNodeView"
  
  def __init__(self):
    super().__init__()

    self.set_has_window(False)
    self.set_size_request(100, 100)

    # Drag dest
    self.drag_dest_set(Gtk.DestDefaults.MOTION, [], Gdk.DragAction.PRIVATE)
    self.drag_dest_set_track_motion(True)
  
  pass
