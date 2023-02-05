#test node tree

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkNodes', '0.1')

from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkNodes
from gi.repository import GdkPixbuf

import struct
import sys

#First, define different node types using GtkNodes.Node as a base type
class ImgSrcNode(GtkNodes.Node):
  __gtype_name__ = 'SrcNode'


  def __init__(self, *args, **kwds) -> None:
    super().__init__(*args, **kwds)

    self.set_label("Image Source")
    self.connect("node_func_clicked",self.remove)

    self.canvas: Gtk.DrawingArea = Gtk.DrawingArea()
    self.canvas.connect("draw", self.draw_image)

    self.add_file_button: Gtk.Button = Gtk.Button(label="Open Image")
    self.add_file_button.connect("clicked", self.open_file)

    self.item_add(self.add_file_button, GtkNodes.NodeSocketIO.DISABLE)
    
  def open_file(self, widget=None):
    dialog = Gtk.FileChooserDialog("Select An Image", None, 
                                  Gtk.FileChooserAction.OPEN,
                                  (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                  Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

    response = dialog.run()
    
    filename = None

    if response == Gtk.ResponseType.OK:
      filename = dialog.get_filename()
      dialog.destroy()
      print(filename)
      self.draw_image(filename)
      return 0 

    dialog.destroy()
      
    

  #information on how to make this comes from 
  def draw_image(self, image_file):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_file)

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

if __name__ == "__main__":
  PluginWindow()
    