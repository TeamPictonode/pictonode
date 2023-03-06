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

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa

gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa
# autopep on


class LoginBox(Gtk.Box):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.set_size_request(300, 350)
        self.set_hexpand(False)
        self.set_vexpand(False)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        # wow was this one fun to figure out lol
        # add background to login box
        self.set_name("my-box")
        css = b'''#my-box
        { 
            background-color: #36454F;
            border-radius: 5;
        }'''

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        context = self.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # header bar w/ "Login"
        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.connect("activate", self.__on_cancel)
        self.cancel_button.connect("clicked", self.__on_cancel)
        header = Gtk.HeaderBar()
        header.set_title("Login")
        header.pack_end(self.cancel_button)
        self.add(header)

        button_padding = 20
        # entry for username
        self.username_entry = Gtk.Entry()
        self.username_entry.connect("activate", self.__username_activate)
        self.username_entry.set_margin_left(button_padding)
        self.username_entry.set_margin_right(button_padding)

        # entry for password,
        # user get_invisible_char to hide input,
        # eye icon for showing or hiding the chars - set_icon_from_pixbuf
        self.password_entry = Gtk.Entry()
        self.password_entry.connect("activate", self.__password_activate)
        self.password_entry.set_margin_left(button_padding)
        self.password_entry.set_margin_right(button_padding)

        # login button
        self.login_button = Gtk.Button(label="Login")
        self.login_button.connect("activate", self.__on_login)
        self.login_button.set_margin_left(button_padding)
        self.login_button.set_margin_right(button_padding)

        # register button that opens website
        self.register_button = Gtk.Button(label="Register")
        self.register_button.connect("activate", self.__on_register)
        self.register_button.set_margin_left(button_padding)
        self.register_button.set_margin_right(button_padding)

        self.pack_start(header, False, False, 0)
        self.pack_start(Gtk.Label(label="Username"), False, False, 10)
        self.pack_start(self.username_entry, False, False, 10)
        self.pack_start(Gtk.Label(label="Password"), False, False, 10)
        self.pack_start(self.password_entry, False, False, 10)
        self.pack_start(self.login_button, False, False, 10)
        self.pack_start(self.register_button, False, False, 10)

    def __on_cancel(self, event):
        self.destroy()

    def __on_register(self):
        pass

    def __on_login(self):
        pass

    def __username_activate(self, entry):
        self.password_entry.grab_focus()

    def __password_activate(self, entry):
        self.login_button.grab_focus()

    def __on_hide_toggle(self):
        pass


# test stuff

'''
window = Gtk.Window(title="Test Window")
overlay = Gtk.Overlay()
frame = Gtk.Frame()
login = LoginBox(orientation=Gtk.Orientation.VERTICAL, spacing=10)
frame.add(login)
window.add(overlay)
overlay.add_overlay(frame)
window.show_all()
Gtk.main()
'''
