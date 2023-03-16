import os

# autopep8 off
import gi # noqa
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

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # noqa

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa

gi.require_version("GObject", "2.0")
from gi.repository import GObject # noqa
from gi.repository.GdkPixbuf import Pixbuf # noqa

class ProjectToolbar(Gtk.Window):

    def __init__(self, mode="Release"):
        super().__init__()
        self.mode = mode
        self.set_default_size(200, 200)
        self.hints = Gdk.Geometry()
        self.hints.min_width = 128
        self.hints.max_width = 256
        self.hints.min_height = 192
        self.hints.max_height = 512
        #self.__set_size_hints()

        self.liststore = Gtk.ListStore(Pixbuf, str)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_activate_on_single_click(True)
        self.iconview.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_item_width(64)
        self.add(self.iconview)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_title("")
        self.headerbar.set_subtitle("")
        self.headerbar.set_show_close_button(False)
        self.headerbar.set_has_subtitle(False)
        self.set_titlebar(self.headerbar)

        self._projects = []

        self.iconview.connect("selection-changed", self.icon_clicked)
        self.init = True

        self.connect("destroy", Gtk.main_quit)

    def icon_clicked(self, widget: Gtk.IconView):
        if self.mode != "Debug":
            from manager import PictonodeManager

            if len(widget.get_selected_items()) != 0:
                PictonodeManager().set_current_project(self.liststore[widget.get_selected_items()[0]][1])

    def add_project(self, prjname: str, pixbuf: Pixbuf) -> None:
        """Store the prjname aligned with itself in the list store so we have easy removal."""
        if prjname not in self._projects:
            self._projects.append(prjname)
            self.liststore.append([pixbuf, prjname])
            #self.resize(64, len(self._projects) * 64)
            if self.init:
                from manager import PictonodeManager
                self.iconview.select_path(Gtk.TreePath.new_first())
                PictonodeManager().set_current_project(self.liststore[self.iconview.get_selected_items()[0]][1])
                self.init = False

    def remove_project(self, prjname: str) -> None:
        remove_index = self._projects.index(prjname)
        self._projects.pop(remove_index)
        iter = self.liststore.get_iter((remove_index,))
        self.liststore.remove(iter)
        #self.resize(64, len(self._projects) * 64)
    
    def update_project_thumbnail(self, prjname: str, pixbuf: Pixbuf) -> None:
        if prjname in self._projects:
            update_index = self._projects.index(prjname)
            self.liststore[update_index] = [pixbuf, prjname]
            self.resize(pixbuf.get_width() + 24, pixbuf.get_height() * len(self._projects))

    def update_project_name(self, oldprjname: str, newprjname: str) -> None:
        update_index = self._projects.index(oldprjname)
        self._projects[update_index] = newprjname
        pixbuf = self.liststore[update_index][0]
        self.liststore[update_index] = [pixbuf, newprjname]

    def set_username_as_titlebar(self, username):
        self.username_as_title = username
        self.headerbar.set_title(username)

    def __set_size_hints(self) -> None:
        self.set_geometry_hints(None, self.hints, Gdk.WindowHints.MAX_SIZE | Gdk.WindowHints.MIN_SIZE)