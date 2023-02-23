# This file was written by Parker Nelms and Stephen Foster.

import custom_nodes as cn
from manager import *
from httpclient import *
from client import *
import window

import sys
import threading
import os
import json

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

# define screen dimensions for window set up
screen = Gdk.Screen.get_default()
screen_width = screen.get_width()
screen_height = screen.get_height()

# class based on the demo class from the gtknode img.py example


class PluginWindow(object):

    def __init__(self, layers: list):
        self.window: Gtk.Window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.set_border_width(20)
        self.window.set_title("Pictonode")

        # output node lock
        self.has_output_node = False

        # buffer map is used for storing and keeping track 
        # of changes to the buffer
        self.buffer_map = {}

        # set drawables from project
        self.layers = layers

        # make menu bar
        menu_bar = Gtk.MenuBar.new()

        # create menus on the bar
        file_menu = Gtk.Menu.new()

        # TODO: about_menu = Gtk.Menu.new()

        # add menu items to file menu
        file_menu_item = Gtk.MenuItem("File")
        file_menu_item.set_submenu(file_menu)
        menu_bar.append(file_menu_item)

        open_graph_item = Gtk.MenuItem("Open Graph")
        file_menu.append(open_graph_item)

        save_graph_item = Gtk.MenuItem("save")
        file_menu.append(save_graph_item)
        save_graph_item.connect("activate", self.save_graph)

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
        self.image_scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

        # add image to image scrolled window
        # TODO: add zooming and panning - need to do some cairo drawing 
        self.image = Gtk.Image.new_from_file("/tmp/gimp/temp.png")
        self.image.set_hexpand(True)
        self.image.set_vexpand(True)
        self.image_scrolled.add_with_viewport(self.image)

        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        self.image_scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)

        frame.add(scrolled_window)
        image_frame.add(self.image_scrolled)

        self.node_view: GtkNodes.NodeView = GtkNodes.NodeView()
        scrolled_window.add(self.node_view)

        # create context menu in node view
        self.node_view.connect("button-press-event", self.on_button_press)

        # Adjustable panes between image viewport and node_view
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_position(screen_height // 3)
        paned.add1(image_frame)
        paned.add2(frame)

        full_view: Gtk.Box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        full_view.pack_start(menu_bar, False, False, 0)
        full_view.pack_start(image_frame, True, True, 20)
        full_view.pack_start(paned, True, True, 0)

        self.window.add(full_view)

        self.window.connect("destroy", self.do_quit)

        # set window size and show plugin window
        self.window.set_default_size(900, 900)
        self.window.show_all()
        Gtk.main()

    def do_quit(self, widget=None, data=None):
        Gtk.main_quit()
        # can't call sys.exit(0) during plugin runtime if window is closed, it'll kill the whole plugin process
        # sys.exit(0)

    def on_button_press(self, widget, event):
        if event.button == 3:
            # create menu and menu items
            menu = Gtk.Menu()

            submenu_item = Gtk.MenuItem(label="Add Nodes")
            submenu = Gtk.Menu()

            sub_item1 = Gtk.MenuItem(label="Source Node")
            sub_item2 = Gtk.MenuItem(label="Output Node")
            sub_item3 = Gtk.MenuItem(label="Invert Node")
            sub_item4 = Gtk.MenuItem(label="Composite Node")
            sub_item5 = Gtk.MenuItem(label="Blur Node")

            # connect menu items here
            sub_item1.connect("activate", self.add_image_src_node)
            sub_item2.connect("activate", self.add_image_out_node)
            sub_item3.connect("activate", self.add_image_invert_node)
            sub_item4.connect("activate", self.add_image_comp_node)
            sub_item5.connect("activate", self.add_image_blur_node)

            # disable output node option if one already exists
            if self.has_output_node:
                sub_item2.set_sensitive(False)

            # add items to submenu
            submenu.append(sub_item1)
            submenu.append(sub_item2)
            submenu.append(sub_item3)
            submenu.append(sub_item4)
            submenu.append(sub_item5)

            # add submenu to menu item
            submenu_item.set_submenu(submenu)

            # add menu item to menu
            menu.append(submenu_item)

            # make menu popup
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

    def output_node_lock(self, has_out_node: bool):
        ''' User should only ever be allowed one output node at any time '''

        if has_out_node:
            self.has_output_node = True
        else:
            self.has_output_node = False

    def add_image_src_node(self, widget=None):
        self.node_view.add(cn.ImgSrcNode(self))
        self.node_view.show_all()

    def add_image_out_node(self, widget=None):
        self.node_view.add(cn.OutputNode(self))
        self.node_view.show_all()

    def add_image_invert_node(self, widget=None):
        self.node_view.add(cn.InvertNode(self))
        self.node_view.show_all()

    def add_image_comp_node(self, widget=None):
        self.node_view.add(cn.CompositeNode(self))
        self.node_view.show_all()

    def add_image_blur_node(self, widget=None):
        self.node_view.add(cn.BlurNode(self))
        self.node_view.show_all()

    def set_node_view(self, new_nv: GtkNodes.NodeView):
        self.node_view = new_nv
        self.node_view.show_all()

    def save_graph(self, widget=None):

        # TODO: add json with attributes for each node

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

    def display_output(self):
        '''
        Handles drawing a Gegl Buffer to the main display
        Meant to be called by an output node object
        '''

        # TODO: draw checker pattern with same dimensions as image
        # Draw image over the checkered background

        # Create Gtk.Image from file (to change to pixbuf later)
        self.image.set_from_file("/tmp/gimp/temp.png")
