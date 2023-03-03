# autopep8 off
import gi # noqa

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # noqa

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf # noqa

class ProjectToolbar(Gtk.Window):

    def __init__(self):
        super().__init__()
        
        self.set_default_size(200, 200)
        self.hints = Gdk.Geometry()
        self.hints.min_width = 128
        self.hints.max_width = 256
        self.hints.min_height = 192
        self.hints.max_height = 512
        self.__set_size_hints()

        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_activate_on_single_click(True)
        self.iconview.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.iconview.set_model(self.liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_item_width(64)
        self.add(self.iconview)

        self._projects = []

        self.iconview.connect("selection-changed", self.icon_clicked)
        self.init = True

        self.connect("destroy", Gtk.main_quit)

    def icon_clicked(self, widget: Gtk.IconView):
        from manager import PictonodeManager

        if len(widget.get_selected_items()) != 0:
            PictonodeManager().set_current_project(self.liststore[widget.get_selected_items()[0]][1])

    def add_project(self, prjname: str, pixbuf: GdkPixbuf.Pixbuf) -> None:
        """Store the prjname aligned with itself in the list store so we have easy removal."""
        self._projects.append(prjname)
        self.liststore.append([pixbuf, prjname])
        
        if self.init:
            self.iconview.select_path(Gtk.TreePath.new_first())
            self.init = False

    def remove_project(self, prjname: str) -> None:
        remove_index = self._projects.index(prjname)
        self._projects.pop(remove_index)
        self.liststore.pop(remove_index)
    
    def update_project_thumbnail(self, prjname: str, pixbuf: GdkPixbuf.Pixbuf) -> None:
        update_index = self._projects.index(prjname)
        self.liststore[update_index] = [pixbuf, prjname]

    def update_project_name(self, oldprjname: str, newprjname: str) -> None:
        update_index = self._projects.index(oldprjname)
        self._projects[update_index] = newprjname
        pixbuf = self.liststore[update_index][0]
        self.liststore[update_index] = [pixbuf, newprjname]

    def __set_size_hints(self) -> None:
        self.set_geometry_hints(None, self.hints, Gdk.WindowHints.MAX_SIZE | Gdk.WindowHints.MIN_SIZE)