import os
import json
import urllib.parse
import urllib.request

# autopep8 off
import gi

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

        self.cancel_register_button = Gtk.Button(label="To Login")
        self.cancel_register_button.connect("activate", self.__on_register_cancel)
        self.cancel_register_button.connect("clicked", self.__on_register_cancel)

        header = Gtk.HeaderBar()
        header.set_title("Login")
        header.pack_start(self.cancel_register_button)
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


        #realname entry label

        self.realname_label = Gtk.Label(label="Name")

        # entry for realname,
        # hidden to user until register button,
        # is used
        self.realname_entry = Gtk.Entry()
        self.realname_entry.connect("activate", self.__realname_activate)
        self.realname_entry.set_margin_left(button_padding)
        self.realname_entry.set_margin_right(button_padding)

        # login button
        self.login_button = Gtk.Button(label="Login")
        self.login_button.connect("activate", self.__on_login)
        self.login_button.connect("clicked", self.__on_login)
        self.login_button.set_margin_left(button_padding)
        self.login_button.set_margin_right(button_padding)

        # register button that opens website
        self.register_button = Gtk.Button(label="Register")
        self.register_button.connect("activate", self.__on_register)
        self.register_button.connect("clicked", self.__on_register)
        self.register_button.set_margin_left(button_padding)
        self.register_button.set_margin_right(button_padding)

        self.pack_start(header, False, False, 0)
        self.pack_start(self.realname_label, False, False, 10)
        self.pack_start(self.realname_entry, False, False, 10)

        self.pack_start(Gtk.Label(label="Username"), False, False, 10)
        self.pack_start(self.username_entry, False, False, 10)
        self.pack_start(Gtk.Label(label="Password"), False, False, 10)
        self.pack_start(self.password_entry, False, False, 10)
        self.pack_start(self.login_button, False, False, 10)
        self.pack_start(self.register_button, False, False, 10)

        self.url = "https://pictonode.com/api"
        self.is_registering = False


    def __on_cancel(self, event):
        self.destroy()

    def __on_register_cancel(self, event):
        self.is_registering = False
        self.login_button.show()
        self.realname_label.hide()
        self.realname_entry.hide()
        self.cancel_register_button.hide()

    def __on_register(self, event):
        if not self.is_registering:
            self.is_registering = True
            self.login_button.hide()
            self.realname_label.show()
            self.realname_entry.show()
            self.cancel_register_button.show()
            return

        if self.is_registering:
            realname = self.realname_entry.get_text()
            username = self.username_entry.get_text()
            password = self.password_entry.get_text()
            print(realname, username, password)
        
            data_raw = {"username":username,
                    "password":password,
                    "realname":realname}

            data_as_json = json.dumps(data_raw).encode("utf-8")
            headers = {"Content-Type": "application/json"}

            req = urllib.request.Request(self.url+"/register", data_as_json, headers,method='POST')

            try:
                response = urllib.request.urlopen(req)
                print("register_response", response.status)
            except Exception as e:
                print(e)

    def __on_login(self, event):
        username = self.username_entry.get_text()
        password = self.password_entry.get_text()
        print(username, password)
        
        data_raw = {"username":username,
                    "password":password}

        data_as_json = json.dumps(data_raw).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(self.url+"/login", data_as_json, headers,method='POST')

        try:
            response = urllib.request.urlopen(req)
            if response.status == 200:
                print("login_response", response.status)
                self.destroy()
                
        except Exception as e:
            print(e)

    def hide_register(self):
        self.realname_label.hide()
        self.realname_entry.hide()
        self.cancel_register_button.hide()
        
    def __username_activate(self, entry):
        self.password_entry.grab_focus()

    def __password_activate(self, entry):
        self.login_button.grab_focus()

    def __realname_activate(self, entry):
        self.username_entry.grab_focus()

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
