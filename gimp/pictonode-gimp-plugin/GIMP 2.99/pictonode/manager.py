from typing import Tuple
import os
import configparser
import window
import threading

# autopep8 off
import gi  # noqa
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

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa
from gi.repository import Gtk # noqa

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa

gi.require_version("GObject", "2.0")
from gi.repository import GObject # noqa
from gi.repository.GdkPixbuf import Pixbuf # noqa

gi.require_version("cairo", "1.0")
from gi.repository import cairo # noqa

# autopep8 on


"""Ensure object __calls__ are threadsafe to always return the same class instance"""
_cls_lock = threading.Lock()
class SingletonConstruction(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            global _cls_lock
            with _cls_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(SingletonConstruction, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


"""Ensure object methods mutating the manager are thread safe"""
_pm_lock = threading.RLock()
def threadsafe(fn):
    def new(*args, **kwargs):
        with _pm_lock:
            try:
                r = fn(*args, **kwargs)
            except Exception as e:
                raise e
        return r
    return new


class PictonodeManager(metaclass=SingletonConstruction):
    def init(self, procedure, run_mode, image, n_drawables, drawables, args, run_data):
        self.procedure = procedure
        self.run_mode = run_mode
        self.image = image
        self.n_drawables = n_drawables
        self.drawables = drawables
        self.args = args
        self.run_data = run_data

        self.settings = {}
        self.local_projects = {}
        self.initial_image = image

        self.settings_ini = {}
        self.projects_ini = {}
        self.settings_ini_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/cache/settings.ini")
        self.projects_ini_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "/cache/projects.ini")
        self.__load_settings_ini()
        self.__load_projects_ini()

        self.images_with_xcf = []
        self.images_without_xcf = []
        self.__update_xcf_image_association()

        for img in self.images_with_xcf:
            self.__add_local_project(img)

        self.main_window: window.PluginWindow

    def run(self):

        ''' This run() will be gutted just checking out some pocs for parker'''
        theme_name = "Yaru"
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-theme-name", theme_name)

        win = Gtk.Window()
        win.set_default_size(128, 256)
        win.set_title("Projects")

        hints = Gdk.Geometry()
        hints.min_width = 128
        hints.max_width = 256
        hints.min_height = 192
        hints.max_height = 512

        win.set_geometry_hints(None, hints, Gdk.WindowHints.MAX_SIZE | Gdk.WindowHints.MIN_SIZE)
        liststore = Gtk.ListStore(Pixbuf, str)
        iconview = Gtk.IconView.new()
        iconview.set_model(liststore)
        iconview.set_pixbuf_column(0)
        iconview.set_text_column(1)
        iconview.set_item_width(64)

        layers = self.image.list_layers()
        print(layers)

        frame = Gtk.Frame.new()
        scrolled_window = Gtk.ScrolledWindow(hexpand=False, vexpand=True)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        frame.add(scrolled_window)
        scrolled_window.add(iconview)
        win.add(frame)

        icons = []
        for img in self.images_with_xcf:
            icons.append(os.path.splitext(os.path.basename(img.get_xcf_file().get_path()))[0])

        for i, img in enumerate(self.images_with_xcf):
            # pixbuf = Gtk.IconTheme.get_default().load_icon(icon, 64, 0)
            pixbuf = img.get_thumbnail(64, 64, 1)
            liststore.append([pixbuf, icons[i]])

        headerbar = Gtk.HeaderBar()
        headerbar.set_title("")
        headerbar.set_subtitle("")
        headerbar.set_show_close_button(False)
        headerbar.set_has_subtitle(False)

        win.set_titlebar(headerbar)
        # win.add(iconview)
        win.connect("destroy", Gtk.main_quit)
        win.show_all()
        # GimpUi.init("pictonode.py")
        self.main_window = window.PluginWindow(self.image.list_layers())
        Gtk.main()
        # icon toolbar
        pass

    # we should disambiguate between loaded local projects and unloaded

    @threadsafe
    def __add_local_project(self, image):
        if image in self.images_with_xcf:
            xcfpath = image.get_xcf_file().get_path()
            name, ext = os.path.splitext(os.path.basename(xcfpath))
            self.local_projects.update({name:xcfpath})
        self.__update_projects_ini()

    @threadsafe
    def __load_local_project(self, name):
        if name in self.local_projects.keys():
            print(self.local_projects[name])
            fn = Gio.File.new_for_path(self.local_projects[name])
            image = Gimp.file_load(Gimp.RunMode.INTERACTIVE, fn)
            #image = Gimp.get_pdb().run_procedure("gimp-file-load", [GObject.Value(Gimp.RunMode, Gimp.RunMode.INTERACTIVE), GObject.Value(Gio.File, fn)])
            display = Gimp.get_pdb().run_procedure("gimp-display-new", [GObject.Value(Gimp.Image, image)])
            #Gimp.get_pdb().run_procedure("gimp-display-present", [GObject.Value(Gimp.Display, display)])
            image.clean_all()
            self.images_with_xcf.append(image)
    @threadsafe
    def __update_settings_ini(self):
        self.settings_ini["SETTINGS"] = self.settings
        # Plus any other sections to update
        self.__save_settings_ini()

    @threadsafe
    def __update_projects_ini(self):
        self.projects_ini["PROJECTS"] = self.local_projects
        # Plus any other sections to update
        self.__save_projects_ini()

    @threadsafe
    def __load_settings_ini(self):
        settings_ini = configparser.SafeConfigParser()
        settings_ini.read(self.settings_ini_path)
        self.settings_ini = settings_ini
        try:
            self.settings = dict(self.settings_ini["SETTINGS"])
        except Exception as e:
            if isinstance(e, KeyError):
                self.__save_settings_ini(default=True)
                self.__load_settings_ini()

    @threadsafe
    def __load_projects_ini(self):
        projects_ini = configparser.SafeConfigParser()
        projects_ini.read(self.projects_ini_path)
        self.projects_ini = projects_ini
        try:
            self.local_projects = dict(self.projects_ini["PROJECTS"])
        except Exception as e:
            if isinstance(e, KeyError):
                self.__save_projects_ini(default=True)
                self.__load_projects_ini()

    @threadsafe
    def __save_settings_ini(self, default=False):
        os.makedirs(os.path.dirname(self.settings_ini_path), exist_ok=True)
        with open(self.settings_ini_path, "w") as ini:
            if default:
                default = configparser.SafeConfigParser()
                default["SETTINGS"] = {}
                default.write(ini)
            else:
                self.settings_ini.write(ini)

    @threadsafe
    def __save_projects_ini(self, default=False):
        os.makedirs(os.path.dirname(self.projects_ini_path), exist_ok=True)
        with open(self.projects_ini_path, "w") as ini:
            if default:
                default = configparser.SafeConfigParser()
                default["PROJECTS"] = {}
                default.write(ini)
            else:
                self.projects_ini.write(ini)

    @threadsafe
    def __update_xcf_image_association(self):
        self.images_with_xcf = set(
            filter(lambda img: img.get_xcf_file(), Gimp.list_images()))
        self.images_without_xcf = set(
            Gimp.list_images()) - self.images_with_xcf

        self.images_with_xcf = list(self.images_with_xcf)
        self.images_without_xcf = list(self.images_without_xcf)

    @threadsafe
    def __image_xcf_association_to_str(self):
        msg = f"Images associated with an xcf: {len(self.images_with_xcf)}\n" 
        for i, img in enumerate(self.images_with_xcf):
            msg += f"{i + 1}: {img.get_xcf_file().get_path()}\n"
        msg += f"Images NOT associated with an xcf: {len(self.images_without_xcf)}\n"
        for i, img in enumerate(self.images_without_xcf):
            msg += f"{i + 1}: {img.get_file().get_path()}\n"
        return msg
    
    @threadsafe
    def __local_projects_to_str(self):
        msg = f"Registered local projects: {len(self.local_projects)}\n"
        for i, (name, path) in enumerate(self.local_projects.items()):
            msg += f"{i + 1}: {name} @ {path}\n"
        return msg
    
    @threadsafe
    def __associate_images_with_xcf(self):
        for img in self.images_without_xcf:
            self.__save_image_to_xcf_dialog(img)

    @threadsafe
    def __save_image_to_xcf_dialog(self, image):
        save_dialog = Gtk.FileChooserDialog(
            "Save unsaved image to xcf",
            None,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL,
             Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE,
             Gtk.ResponseType.OK))

        # require .xcf file types
        file_type_filter = Gtk.FileFilter()
        file_type_filter.set_name(".xcf files")
        file_type_filter.add_pattern("*.xcf")

        save_dialog.add_filter(file_type_filter)
        save_dialog.set_do_overwrite_confirmation(True)

        while (True):
            response = save_dialog.run()

            if response == Gtk.ResponseType.OK:

                fn = save_dialog.get_filename()
                fn = sanitize_filepath(fn)

                if filepath_is_valid(fn):
                    fo = Gio.File.new_for_path(fn)
                    #Gimp.file_save(self.run_mode, image, image.list_layers(), f)
                    Gimp.get_pdb().run_procedure("gimp-xcf-save", [GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
                                                                   GObject.Value(
                                                                       Gimp.Image, image),
                                                                   GObject.Value(GObject.TYPE_INT, len(
                                                                       image.list_layers())),
                                                                   GObject.Value(Gimp.ObjectArray.new(
                                                                       Gimp.Drawable, image.list_layers(), False)),
                                                                   GObject.Value(Gio.File, fo)])
                    break
                else:
                    # should display and error popup here
                    pass
            elif response == Gtk.ResponseType.CANCEL:
                break

        save_dialog.destroy()

    @threadsafe
    def __load_image_from_xcf(self, filepath):
        pass

    def __repr__(self):
        return self.__image_xcf_association_to_str() + '\n' + self.__local_projects_to_str()


def is_xcf(filepath):
    base, ext = os.path.splitext(filepath)
    ext.lower()
    return ext == ".xcf"


def sanitize_filepath(filepath):
    if not is_xcf(filepath):
        return filepath + ".xcf"
    return filepath


def filepath_is_valid(filepath):
    path = os.path.abspath(filepath)
    #should change this, we shouldn't try and access members directly
    #even if its just a read
    return not (path in PictonodeManager().local_projects)
