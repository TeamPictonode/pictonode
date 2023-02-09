# This file was written by Parker Nelms and Stephen Foster.

import custom_nodes as cn

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

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa
# autopep8 on


css = b"""
frame {
  background-color: #D3D3D3
}
"""

# class based on the demo class from the gtknode img.py example


class PluginWindow(object):

    def __init__(self):
        self.window: Gtk.Window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.set_border_width(20)
        self.window.set_title("Pictonode")

        # make menu bar
        menu_bar = Gtk.MenuBar.new()

        # create menus on the bar
        file_menu = Gtk.Menu.new()
        about_menu = Gtk.Menu.new()

        # add menu items to file menu
        file_menu_item = Gtk.MenuItem("File")
        file_menu_item.set_submenu(file_menu)
        menu_bar.append(file_menu_item)

        open_graph_item = Gtk.MenuItem("Open Graph")
        file_menu.append(open_graph_item)

        save_graph_item = Gtk.MenuItem("save")
        file_menu.append(save_graph_item)
        save_graph_item.connect("activate", self.save_graph)

        # create node menu
        hbox: Gtk.Box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        # add node options
        img_src_button: Gtk.Button = Gtk.Button(label="Add Image Source Node")
        img_src_button.connect("clicked", self.add_image_src_node)
        hbox.add(img_src_button)

        img_out_button: Gtk.Button = Gtk.Button(label="Add Image Output Node")
        img_out_button.connect("clicked", self.add_image_out_node)
        hbox.add(img_out_button)

        # create a css provider to change the frame background
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)

        # add frame widget
        frame = Gtk.Frame.new()
        image_frame = Gtk.Frame.new()

        # get style context for the frame and adds the css provider to it
        style_context = frame.get_style_context()
        style_context.add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # adds scrolled window in which the whole plugin will exist
        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        image_scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        image_scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)

        frame.add(scrolled_window)
        image_frame.add(image_scrolled)

        self.node_view: GtkNodes.NodeView = GtkNodes.NodeView()
        scrolled_window.add(self.node_view)

        # Adjustable panes between image viewport and node_view
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.add1(image_frame)
        paned.add2(frame)

        full_view: Gtk.Box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        full_view.pack_start(menu_bar, False, False, 0)
        full_view.pack_start(image_frame, True, True, 20)
        full_view.pack_start(paned, True, True, 0)
        full_view.pack_start(hbox, False, False, 0)

        self.window.add(full_view)

        self.window.connect("destroy", self.do_quit)

        # set window size and show plugin window
        self.window.set_default_size(900, 500)
        self.window.show_all()
        Gtk.main()

    def add_node(self, node_type: GtkNodes.Node, widget=None):
        self.node_view.add(node_type)
        self.node_view.show_all()

    def do_quit(self, widget=None, data=None):
        Gtk.main_quit()
        sys.exit(0)

    def save(self):
        self.node_view.save("node_structure.xml")

    def add_image_src_node(self, widget=None):
        self.node_view.add(cn.ImgSrcNode())
        self.node_view.show_all()

    def add_image_out_node(self, widget=None):
        self.node_view.add(cn.OutputNode())
        self.node_view.show_all()

    def set_node_view(self, new_nv: GtkNodes.NodeView):
        self.node_view = new_nv
        self.node_view.show_all()

    def save_graph(self, widget=None):
        save_dialog = Gtk.FileChooserDialog(
            "Save Node Graph",
            self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE,
             Gtk.ResponseType.OK))

        # require .xml file types
        file_type_filter = Gtk.FileFilter()
        file_type_filter.set_name(".xml files")
        file_type_filter.add_pattern("*.xml")

        save_dialog.add_filter(file_type_filter)

        # run the window
        response = save_dialog.run()

        # if ok response, that means a file was chosen, save the node graph as
        # that file
        if response == Gtk.ResponseType.OK:
            fn = save_dialog.get_filename()
            save_dialog.destroy()
            self.node_view.save(fn)
            return None

        # close the dialog
        save_dialog.destroy()
