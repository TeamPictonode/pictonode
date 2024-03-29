# This file was written by Parker Nelms and Stephen Foster.

import custom_nodes as cn
from manager import *
from httpclient import *
from client import *
from json_generator import *
from json_interpreter import *
from login_window import LoginBox
from about import AboutDialog

import datetime
import sys
import threading
import os
import json
import zipfile

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

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf  # noqa

gi.require_version("GLib", "2.0")
from gi.repository import GLib # noqa

# autopep8 on

# found at https://stackoverflow.com/a/32861765
css = b"""
frame {
  background-color: white;
  background-image:
    linear-gradient(to right, rgba(184,184,184,0.5) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(184,184,184,0.5) 1px, transparent 1px);
  background-size: 10px 10px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}
"""

# found at https://stackoverflow.com/a/35362074
css_image_background = b"""
image {
  background-color: white;
  background-image: linear-gradient(45deg, #c0c0c0 25%, transparent 25%),
    linear-gradient(-45deg, #c0c0c0 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #d0d0d0 75%),
    linear-gradient(-45deg, transparent 75%, #d0d0d0 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}
"""

# define screen dimensions for window set up
screen = Gdk.Screen.get_default()
screen_width = screen.get_width()
screen_height = screen.get_height()

# class based on the demo class from the gtknode img.py example


class PluginWindow(Gtk.Window):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_target_file = ""
        self.set_border_width(20)
        self.set_title("Pictonode")

        # create overlay so that widgets can popup on UI
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)

        # bool for adding nodes in context menu 
        self.is_from_context_menu = True

        # variables used for image zooming
        self.pixbuf = None
        self.width_mult = 1
        self.height_mult = 1

        # reset preview image
        if os.path.isfile("/tmp/gimp/temp.png"):
            os.remove("/tmp/gimp/temp.png")

        # output node lock
        self.has_output_node = False

        # buffer map is used for storing and keeping track
        # of changes to the buffer
        self.buffer_map = {}

        # set drawables from project
        self.layers = []

        # make menu bar
        menu_bar = Gtk.MenuBar.new()

        # create menus on the bar
        file_menu = Gtk.Menu.new()
        settings_menu = Gtk.Menu.new()
        about_menu = Gtk.Menu.new()

        # TODO: about_menu = Gtk.Menu.new()

        # add menu items to file menu
        file_menu_item = Gtk.MenuItem("File")
        settings_menu_item = Gtk.MenuItem("Settings")
        about_menu_item = Gtk.MenuItem("About")

        file_menu_item.set_submenu(file_menu)
        settings_menu_item.set_submenu(settings_menu)
        about_menu_item.set_submenu(about_menu)

        menu_bar.append(file_menu_item)
        menu_bar.append(settings_menu_item)
        menu_bar.append(about_menu_item)

        open_graph_item = Gtk.MenuItem("Open Node Graph")
        open_graph_item.connect("activate", self.open_graph)
        file_menu.append(open_graph_item)

        save_graph_item = Gtk.MenuItem("Save Graph as")
        file_menu.append(save_graph_item)
        save_graph_item.connect("activate", self.save_graph)

        # menu itme for saving picto projects
        save_project_item = Gtk.MenuItem("Save Project as")
        file_menu.append(save_project_item)
        save_project_item.connect("activate", self.save_project)
        
        clear_startup_graph_item = Gtk.MenuItem("Clear Startup Graph")
        clear_startup_graph_item.connect("activate", self.clear_startup_graph)
        settings_menu.append(clear_startup_graph_item)

        login_item = Gtk.MenuItem("Login")
        about_item = Gtk.MenuItem("About")
        about_menu.append(login_item)
        about_menu.append(about_item)
        login_item.connect("activate", self.login)
        about_item.connect("activate", self.about)

        # create a css provider to change the frame background
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)

        # add frame widget
        frame = Gtk.Frame.new()
        image_frame = Gtk.Frame.new()

        # get style context for the frame and add the css provider to it
        style_context = frame.get_style_context()
        style_context.add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # adds scrolled window in which the whole plugin will exist
        scrolled_window = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.image_scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

        # create a css provider to change the image background
        image_css_provider = Gtk.CssProvider()
        image_css_provider.load_from_data(css_image_background)

        # add image to image scrolled window
        # TODO: add zooming and panning - need to do some cairo drawing
        self.image = Gtk.Image.new_from_file("/tmp/gimp/temp.png")

        # get style context for the image and add the css provider to it
        image_style_context = self.image.get_style_context()
        image_style_context.add_provider(
            image_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.image_scrolled.add_with_viewport(self.image)
        self.image_scrolled.add_events(Gdk.EventMask.SCROLL_MASK)
        self.image_scrolled.connect('scroll-event', self.on_scroll)

        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        self.image_scrolled.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)

        frame.add(scrolled_window)
        image_frame.add(self.image_scrolled)

        self.node_view: GtkNodes.NodeView = GtkNodes.NodeView()
        cn.g_NodeView = self.node_view
        scrolled_window.add(self.node_view)

        # create context menu in node view
        self.node_view.connect("button-press-event", self.on_button_press)

        # Adjustable panes between image viewport and node_view
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_position(screen_height // 2)
        paned.add1(image_frame)
        paned.add2(frame)
        paned.set_wide_handle(True)

        full_view: Gtk.Box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        full_view.pack_start(menu_bar, False, False, 0)
        full_view.pack_start(image_frame, True, True, 20)
        full_view.pack_start(paned, True, True, 0)

        self.overlay.add(full_view)


        # set window size and show plugin window
        self.set_default_size((screen_width * .75), (screen_height * .75))

        self.save_semaphore = threading.Semaphore()
        self.serialization = None
        cn.g_Window = self

        def do_quit(_):
            from manager import PictonodeManager
            PictonodeManager().notify_quit()

        self.connect("destroy", do_quit)


    def load_graph(self, filepath):
        for node in self.node_view.get_children():
            # On the last reference of the node widget, destroy is called by Gtk safely
            self.node_view.remove(node)

        if os.path.isfile(filepath):
            with open(filepath) as f:
                self.temp_target_file = os.path.splitext(os.path.basename(filepath))[0]
                json_string = json.load(f)

                self.is_from_context_menu = False

                try:
                    json_interpreter(self.node_view, self, json_string=json_string)
                except Exception as E:
                    print(E)
                
                self.is_from_context_menu = True

                self.set_layers(self.layers)
                
                GLib.idle_add(self.__reset_expand)
                self.node_view.show_all()
        else:
            self.temp_target_file = timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        return None

    def clear_startup_graph(self, widget=None):
        from manager import PictonodeManager
        PictonodeManager().set_startup_graph("")

    def login(self, widget=None):
        # create login overlay
        login_box = LoginBox(orientation=Gtk.Orientation.VERTICAL)
        self.overlay.add_overlay(login_box)
        self.show_all()
        login_box.hide_register()
        login_box.login_error.hide()

    def about(self, widget=None):
        about_dialog = AboutDialog()
        about_dialog.show_all()

    def on_button_press(self, widget, event):
        if event.button == 3:
            # create menu and menu items
            menu = Gtk.Menu()

            submenu_item = Gtk.MenuItem(label="Add Nodes")
            submenu = Gtk.Menu()

            separator = Gtk.SeparatorMenuItem()
            separator.set_margin_top(5)
            separator.set_margin_bottom(5)

            sub_item1 = Gtk.MenuItem(label="Source Node")
            sub_item2 = Gtk.MenuItem(label="Output Node")
            sub_item3 = Gtk.MenuItem(label="Invert Node")
            sub_item4 = Gtk.MenuItem(label="Bright/Contrast")
            sub_item5 = Gtk.MenuItem(label="Blur Node")
            sub_item6 = Gtk.MenuItem(label="Composite Node")
            sub_item7 = Gtk.MenuItem(label="Dropshadow Node")
            sub_item8 = Gtk.MenuItem(label="Waterpixels Node")
            sub_item9 = Gtk.MenuItem(label="Tile Glass Node")
            sub_item10 = Gtk.MenuItem(label="Text Node")

            # connect menu items here
            sub_item1.connect("activate", self.add_image_src_node)
            sub_item2.connect("activate", self.add_image_out_node)
            sub_item3.connect("activate", self.add_image_invert_node)
            sub_item4.connect("activate", self.add_bright_cont_node)
            sub_item5.connect("activate", self.add_image_blur_node)
            sub_item6.connect("activate", self.add_image_comp_node)
            sub_item7.connect("activate", self.add_dropshadow_node)
            sub_item8.connect("activate", self.add_waterpixels_node)
            sub_item9.connect("activate", self.add_tileglass_node)
            sub_item10.connect("activate", self.add_textsrc_node)

            # disable output node option if one already exists
            if self.has_output_node:
                sub_item2.set_sensitive(False)

            # add items to submenu
            submenu.append(sub_item1)
            submenu.append(sub_item2)
            submenu.append(separator)
            submenu.append(sub_item3)
            submenu.append(sub_item4)
            submenu.append(sub_item5)
            submenu.append(sub_item6)
            submenu.append(sub_item7)
            submenu.append(sub_item8)
            submenu.append(sub_item9)
            submenu.append(sub_item10)

            # add submenu to menu item
            submenu_item.set_submenu(submenu)

            # add menu item to menu
            menu.append(submenu_item)

            # make menu popup
            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

        x = threading.Thread(target=self.save_temp)
        x.start()
        #GLib.idle_add(self.save_temp)

    def on_scroll(self, widget, event):
        ''' Scroll event for zooming on image '''

        accel_mask = Gtk.accelerator_get_default_mod_mask()
        print("Mod mask: ", accel_mask)
        if (event.state & accel_mask) == Gdk.ModifierType.CONTROL_MASK:
            direction = event.get_scroll_deltas()[2]

            print("Direction: ", direction)

            if direction > 0:
                # this may cause some slight warping due to rounding errors?
                self.width_mult -= 0.1
                self.height_mult -= 0.1
            else:
                                # this may cause some slight warping due to rounding errors?
                self.width_mult += 0.1
                self.height_mult += 0.1

            self.__draw_zoomed_image()

    def __draw_zoomed_image(self):
        # redraws image based on window's current zoom multiplier
        width = self.pixbuf.get_property("width")
        height = self.pixbuf.get_property("height")
        new_pixbuf = self.pixbuf.scale_simple(int(self.width_mult * width),
                                              (self.height_mult * height),
                                              GdkPixbuf.InterpType.BILINEAR)

        self.image.set_from_pixbuf(new_pixbuf)

    def __reset_expand(self):
        '''fix for visual bug when adding node'''

        for child in self.node_view.get_children():
            if child.get_expanded():
                child.set_expanded(False)
                child.set_expanded(True)
            elif not child.get_expanded():
                child.set_expanded(True)
                child.set_expanded(False)

        return False


    def output_node_lock(self, has_out_node: bool):
        ''' User should only ever be allowed one output node at any time '''

        if has_out_node:
            self.has_output_node = True
        else:
            self.has_output_node = False

    def add_image_src_node(self, widget=None):
        ''' Adds an image source node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.ImgSrcNode(self)
        new_node.set_layers(self.layers)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu: 
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_image_out_node(self, widget=None):
        ''' Adds an image output node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.OutputNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu: 
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_image_invert_node(self, widget=None):
        ''' Adds an invert node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.InvertNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu: 
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_waterpixels_node(self, widget=None):
        ''' Adds an waterpixels node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.WaterpixelNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu: 
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_tileglass_node(self, widget=None):
        ''' Adds an tile glass node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.TileGlassNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu: 
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_image_comp_node(self, widget=None):
        ''' Adds a composite node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.CompositeNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu: 
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_bright_cont_node(self, widget=None):
        ''' Adds a brightness contrast node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.BrightContNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu:
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_image_blur_node(self, widget=None):
        ''' Adds a blur node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.BlurNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu:
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()

    def add_dropshadow_node(self, widget=None):
        ''' Adds a dropshadow node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.DropshadowNode(self)
        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])

        if self.is_from_context_menu:
            GLib.idle_add(self.__reset_expand)

        self.node_view.show_all()
    
    def add_textsrc_node(self, widget=None):
        ''' Adds a text source node at the current cursor position '''

        # create new node and add it to the NodeView widget
        new_node = cn.TextSrcNode(self)

        self.node_view.add(new_node)

        # grab cursor position and move node to it
        position = self.get_cursor_pos()
        new_node.set_property("x", position[0])
        new_node.set_property("y", position[1])


        if self.is_from_context_menu:
            GLib.idle_add(self.__reset_expand)


        self.node_view.show_all()

    def get_cursor_pos(self) -> list:
        pointer = self.node_view.get_display().get_default_seat().get_pointer()
        pos = self.node_view.get_window().get_device_position(pointer)

        return [pos[1], pos[2]]

    def reset_node_view(self):
        self.node_view = GtkNodes.NodeView.new()
        self.node_view.show_all()
        self.show_all()

    def set_layers(self, layers):
        self.layers = layers[:]
        #find all children
        nodes = self.node_view.get_children()
        for node in nodes:
            if isinstance(node, cn.ImgSrcNode):
                print("updating ImgSrcNode")
                node.set_layers(self.layers)

    def save_graph(self, widget=None):

        save_dialog = Gtk.FileChooserDialog(
            "Save Node Graph",
            self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE,
             Gtk.ResponseType.OK))

        # require .json file types
        file_type_filter = Gtk.FileFilter()
        file_type_filter.set_name(".JSON files")
        file_type_filter.add_pattern("*.JSON")

        save_dialog.add_filter(file_type_filter)

        # run the window
        response = save_dialog.run()

        # if ok response, that means a file was chosen, save the node graph as
        # that file
        if response == Gtk.ResponseType.OK:
            from manager import PictonodeManager
            fn = save_dialog.get_filename()[:]

            dictionary = serialize_nodes(self.node_view)

            # credit geeksforgeeks
            with open(fn, "w") as outfile:
                json.dump(dictionary, outfile, indent=2)
                
            PictonodeManager().set_startup_graph(fn)
            self.temp_target_file = os.path.splitext(os.path.basename(fn))[0]

            save_dialog.destroy()
            return None

        # close the dialog
        save_dialog.destroy()

    def save_project(self, widget=None):

        ''' This saves a pictnode project as a .picto which is secretly a .zip file '''

        save_dialog = Gtk.FileChooserDialog(
            "Save Pictonode Project",
            self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE,
             Gtk.ResponseType.OK))

        # require .zip file types
        file_type_filter = Gtk.FileFilter()
        file_type_filter.set_name(".zip files")
        file_type_filter.add_pattern("*.zip")

        save_dialog.add_filter(file_type_filter)

        # run the window
        response = save_dialog.run()

        # if ok response, that means a file was chosen, save the project as
        # that file
        if response == Gtk.ResponseType.OK:

            fn = save_dialog.get_filename()[:]

            dictionary = serialize_nodes(self.node_view)

            pipeline_file = json.dumps(dictionary, indent=2)

            with zipfile.ZipFile(fn, 'w') as myzip:
                myzip.writestr('pipeline.json', pipeline_file.encode('utf-8'))

            save_dialog.destroy()
            return None

        # close the dialog
        save_dialog.destroy()

    def save_temp(self):
        from manager import PictonodeManager

        basename = self.temp_target_file
        new_serialization = serialize_nodes(self.node_view)

        # check lock check go brrrrr
        if self.serialization != new_serialization:
            if self.save_semaphore.acquire():
                if self.serialization != new_serialization:
                    self.serialization = new_serialization
                    temp = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + f"/cache/{basename.replace('-temp', '')}-temp.json")

                    with open(temp, "w") as outfile:
                        json.dump(self.serialization, outfile, indent=2)

                    print(f"{GLib.get_current_time()} - saved")
                    PictonodeManager().set_startup_graph(temp)
                    self.save_semaphore.release()
                else:
                    print(f"{GLib.get_current_time()} - not saved (cached)")
        else:
            print(f"{GLib.get_current_time()} - not saved (cached)")

    def open_graph(self, widget=None):

        open_dialog = Gtk.FileChooserDialog(
            "Open Node Graph",
            self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN,
             Gtk.ResponseType.OK))

        # require .json file types
        file_type_filter = Gtk.FileFilter()
        file_type_filter.set_name(".JSON files")
        file_type_filter.add_pattern("*.JSON")
        file_type_filter.add_pattern("*.json")

        open_dialog.add_filter(file_type_filter)

        # run the window
        response = open_dialog.run()

        # if ok response, that means a file was chosen, load that file
        # then call the json interpreter to build the graph
        if response == Gtk.ResponseType.OK:
            from manager import PictonodeManager
            fn = open_dialog.get_filename()[:]
            
            # delete current node_view nodes
            for node in self.node_view.get_children():
                # On the last reference of the node widget, destroy is called by Gtk safely
                self.node_view.remove(node)

            f = open(fn)
            json_string = json.load(f)

            self.is_from_context_menu = False
            
            try:
                json_interpreter(self.node_view, self, json_string=json_string)
            except Exception as E:
                print(E)
            
            self.is_from_context_menu = True

            PictonodeManager().set_startup_graph(fn)
            self.temp_target_file = os.path.splitext(os.path.basename(fn))[0]

            self.set_layers(self.layers)

            open_dialog.destroy()
            f.close()
            

            GLib.idle_add(self.__reset_expand)
            self.node_view.show_all()

            return None

        # close the dialog
        open_dialog.destroy()

    def display_output(self):
        '''
        Handles drawing a Gegl Buffer to the main display
        Meant to be called by an output node object
        '''

        # TODO: draw checker pattern with same dimensions as image

        # Create Gtk.Image from file (to change to pixbuf later)
        self.image.set_from_file("/tmp/gimp/temp.png")
        self.pixbuf = self.image.get_pixbuf()

        try:
            self.__draw_zoomed_image()
        except:
            pass
