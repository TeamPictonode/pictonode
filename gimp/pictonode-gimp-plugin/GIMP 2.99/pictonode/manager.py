import os
import errno

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

gi.require_version("GtkNodes", "0.1")
from gi.repository import GtkNodes  # noqa

gi.require_version('Gimp', '3.0')
from gi.repository import Gimp  # noqa

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # noqa

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa

gi.require_version("GObject", "2.0")
from gi.repository import GObject # noqa

from typing import Tuple
PictonodeProject = Tuple[int, int]

# autopep8 on

class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        try:
            return self._instance
        except:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError("Singletons must be accessess through instance()")
    
    def __instancecheck__(self, __instance):
        return isinstance(__instance, self._decorated)
    

@Singleton
class PictonodeManager:
    def init(self, procedure, run_mode, image, n_drawables, drawables, args, run_data):
        self.procedure = procedure
        self.run_mode = run_mode
        self.image = image
        self.n_drawables = n_drawables
        self.drawables = drawables
        self.args = args
        self.run_data = run_data
        
        self.local_projects = []
        self.initial_image = image
        self.images_with_xcf = []
        self.images_without_xcf = []
        '''
        /pictonode/config/.config ui
        /pictonode/local/.list_of_local_projects.
        '''
        self.__update_xcf_image_association()
        self.__print_image_xcf_association()

    def __load_local_projects_list(self):
        return [""]
    
    def __update_xcf_image_association(self):
        self.images_with_xcf = set(filter(lambda img: img.get_xcf_file(), Gimp.list_images()))
        self.images_without_xcf = set(Gimp.list_images()) - self.images_with_xcf

    def __print_image_xcf_association(self):
        print("Images associated with an xcf:")
        for i, img in enumerate(self.images_with_xcf):
            print(i + 1, img.get_xcf_file().get_path())
        print("Images NOT associated with an xcf")
        for i, img in enumerate(self.images_without_xcf):
            print(i + 1, img.get_file().get_path())
        
    def __associate_images_with_xcf(self):
        for img in self.images_without_xcf:
            self.__save_image_to_xcf_dialog(img)
    
    def __save__image_to_xcf_dialog(self, image):
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

        while(True):
            response = save_dialog.run()

            if response == Gtk.ResponseType.OK:

                fn = save_dialog.get_filename()
                fn = sanitize_filepath(fn)

                if filepath_is_valid(fn):
                    fo = Gio.File.new_for_path(fn)
                    #Gimp.file_save(self.run_mode, image, image.list_layers(), f)
                    Gimp.get_pdb().run_procedure("gimp-xcf-save", [GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
                                                          GObject.Value(Gimp.Image, image),
                                                          GObject.Value(GObject.TYPE_INT, len(image.list_layers())),
                                                          GObject.Value(Gimp.ObjectArray.new(Gimp.Drawable, image.list_layers(), False)),
                                                          GObject.Value(Gio.File, fo)])
                    break
                else:
                    #should display and error popup here
                    pass
            elif response == Gtk.ResponseType.CANCEL:
                break

        save_dialog.destroy()

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
    return not (path in PictonodeManager.instance().local_projects)