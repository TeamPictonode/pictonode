import os
import sys

if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

class NodeView(Gtk.Container):
    __gtype_name__ = "NodeView"

    def __init__(self, *args, **kwargs):
        self.children = []
        super().__init__()

    def do_add(self, widget):
        self.children.append(widget)
        widget.set_parent(self)

    def do_remove(self, widget):
        self.children.remove(widget)
        widget.unparent()

    def do_child_type(self):
        print("do_child_type()")
        return (Gtk.Widget.get_type())

    def do_forall(self, include_internals, callback, *callback_parameters):
        print("do_forall() self = %x" % id(self))
        if not callback is None:
            for widget in self.children:
                callback(widget, *callback_parameters)

    def do_get_request_mode(self):
        print("do_get_request_mode()")
        return (Gtk.SizeRequestMode.CONSTANT_SIZE)

    def do_get_preferred_height(self):
        print("do_get_preferred_height()")
        result = (50, 50)
        return (result)

    def do_get_preferred_width(self):
        print("do_get_preferred_width()")
        min_width = 0
        nat_width = 0

        for widget in self.children:
            child_min_width, child_nat_width = widget.get_preferred_width()
            min_width = min_width + child_min_width
            nat_width = nat_width + child_nat_width

        return (min_width, nat_width)

    def do_size_allocate(self, allocation):
        print("do_size_allocate()")
        child_allocation = Gdk.Rectangle()

        self.set_allocation(allocation)

        if self.get_has_window():
            if self.get_realized():
                self.get_window().move_resize(allocation.x, allocation.y, allocation.width, allocation.height)

        for widget in self.children:
            if widget.get_visible():
                min_size, nat_size = widget.get_preferred_size()

                child_allocation.x = 0
                child_allocation.y = 0

                if not widget.get_has_window():
                    child_allocation.x = child_allocation.x + allocation.x
                    child_allocation.y = child_allocation.x + allocation.x

                child_allocation.width = min_size.width
                child_allocation.height = min_size.height

                widget.size_allocate(child_allocation)

    def do_realize(self):
        print("do_realize()")
        allocation = self.get_allocation()

        attr = Gdk.WindowAttr()
        attr.window_type = Gdk.WindowType.CHILD
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.window_class = Gdk.WindowWindowClass.INPUT_OUTPUT
        attr.visual = self.get_visual()
        attr.event_mask = self.get_events() | (Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.TOUCH_MASK | Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)

        WAT = Gdk.WindowAttributesType
        mask = WAT.X | WAT.Y

        window = Gdk.Window(self.get_parent_window(), attr, mask);

        self.set_window(window)
        self.register_window(window)
        self.set_realized(True)

    def do_draw(self, cr):
        allocation = self.get_allocation()
        Gtk.render_background(self.get_style_context(), cr, 0, 0, allocation.width, allocation.height)

        for widget in self.children:
            self.propagate_draw(widget, cr)
    '''
    def __init__(self):
        super().__init__()
        #self.widget = Gtk.Widget()
        #self.container = Gtk.Container()

        #need to add virtual function to realize container class,
        #line 308 https://github.com/aluntzer/gtknodes/blob/master/src/gtknodeview.c
        #line 959 https://github.com/AliensGroup/Gtk.NodeGraph/blob/master/Gtk.NodeGraph/NodeView.cs
        #virtual functions in python
        
        #container template above, refactor based on above links
    '''


