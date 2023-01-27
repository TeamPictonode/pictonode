# GNU AGPL v3 License
# Written by Stephen Foster and John Nunley, derived from code by aluntzer and AliensGroup

import sys
import os
if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

from collections.abc import List
from types import NoneType
from typing import Union

# autopep8: off
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject
# autopep8: on


class _NodeChild:
    item: Gtk.Widget
    socket: Gtk.Widget

    input_id: int


class Node(Gtk.Box):
    __event_window: Union[Gdk.Window, NoneType]
    __children: List[Gtk.Widget]

    id = GObject.Property(type=int, default=0)
    x = GObject.Property(type=int, default=0)
    y = GObject.Property(type=int, default=0)
    width = GObject.Property(type=int, default=0)
    height = GObject.Property(type=int, default=0)
    socketid = GObject.Property(type=int, default=0)
    inputid = GObject.Property(type=int, default=0)

    __socket_radius: float
    __func_width: int
    __func_height: int
    __priv_width: int
    __priv_height: int

    __padding_top: int
    __padding_bottom: int
    __padding_left: int
    __padding_right: int

    __margin_top: int
    __margin_bottom: int
    __margin_left: int
    __margin_right: int

    __icon_name: str
    __expander: Gtk.Expander
    __expander_blocked: bool
    __last_expanded: bool
    __allocation: Gdk.Allocation

    __gsignals__ = {
        "node-drag-begin": (GObject.SignalFlags.RUN_LAST, None, (int, int)),
        "node-drag-end": (GObject.SignalFlags.RUN_LAST, None, ()),
        "node-func-clicked": (GObject.SignalFlags.RUN_LAST, None, ()),
        "node-socket-connect": (GObject.SignalFlags.RUN_LAST, None, (Gtk.Widget, Gtk.Widget)),
        "node-socket-disconnect": (GObject.SignalFlags.RUN_LAST, None, (Gtk.Widget, Gtk.Widget)),
        "node-socket-destroyed": (GObject.SignalFlags.RUN_LAST, None, (Gtk.Widget)),
    }

    def __init__(self):
        super().__init__()
        self.attr = Gdk.WindowAttr()
        self.__event_window = None
        self.__children = []

        self.__func_width = 20
        self.__func_height = 20
        self.__priv_width = 20
        self.__priv_height = 20

        self.__socket_radius = 8.0

        self.__padding_bottom = 10
        self.__padding_left = 10
        self.__padding_right = 10
        self.__padding_top = 10

        self.__margin_top = 8
        self.__margin_bottom = 8
        self.__margin_left = 8
        self.__margin_right = 8

        self.__icon_name = "edit-delete-symbolic"

        self.set_homogeneous(False)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.__expander = Gtk.Expander.new("Node")
        self.__expander.set_expanded(True)
        self.pack_start(self.expander, False, False, 10)

        self.__expander_blocked = False
        self.__last_expanded = True
        self.__allocation = Gdk.Allocation()

        self.set_has_window(False)

    # TODO: Get/Set properties

    def do_map(self):
        super().do_map()

        if self.__event_window is not None:
            self.__event_window.show()

    def do_unmap(self):
        if self.__event_window is not None:
            self.__event_window.hide()

        super().do_unmap()

    def do_realize(self):
        super().do_realize()
        self.set_realized(True)
        self.set_window(self.get_parent_window())

        allocation = self.get_allocation()

        attributes = Gdk.WindowAttr()
        attributes.window_type = Gdk.WindowType.CHILD
        attributes.x = allocation.x
        attributes.y = allocation.y
        attributes.width = allocation.width
        attributes.height = allocation.height
        attributes.visual = self.get_visual()
        attributes.window_class = Gdk.WindowWindowClass.INPUT_OUTPUT
        attributes.event_mask = (Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK |
                                 Gdk.EventMask.TOUCH_MASK | Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        attr_mask = Gdk.WindowAttributesType.X | Gdk.WindowAttributesType.Y

        self.__event_window = Gdk.Window(
            self.get_window(), self.attr, attr_mask)
        self.register_window(self.__event_window)

        for child in self.__children:
            child.item.set_parent_window(self.__event_window)
            child.socket.set_parent_window(self.__event_window)

        self.__expander.set_parent_window(self.__event_window)

    def do_unrealize(self):
        if self.__event_window is not None:
            self.unregister_window(self.__event_window)
            self.__event_window.destroy()
            self.__event_window = None

        # TODO: Activate_id removal

        super().do_unrealize()

    def do_size_allocate(self, allocation):
        pass

    def do_draw(self, cr):
        print("node - do draw")
        allocation = self.get_allocation()
        allocation.x = self.margin_left
        allocation.y = self.margin_top
        allocation.width -= self.margin_left + self.margin_right
        allocation.height -= self.margin_top + self.margin_bottom
        self.draw_frame(cr, allocation)
        super().draw(cr)
        return Gdk.EVENT_PROPAGATE

    def draw_frame(self, cr, allocation):
        print("node - draw_frame")
        c = self.get_style_node()
        Gtk.StyleContext.save(c)
        Gtk.render_background(c, cr, allocation.x, allocation.y,
                              allocation.width, allocation.height)
        Gtk.render_frame(c, cr, allocation.x, allocation.y,
                         allocation.width, allocation.height)
        Gtk.StyleContext.restore(c)
        self.rect_x = allocation.x + allocation.width - 25
        self.rect_y = allocation.y + self.padding_top

        # if icon_name
        it = Gtk.IconTheme.get_default()
        pb = Gtk.IconTheme.load_icon(it, self.icon_name, self.rect_y, 0, 0)
        Gdk.Cairo.save(cr)
        Gdk.Cairo.set_source_pixbuf(cr, pb, self.rect_x, self.rect_y)
        Gdk.Cairo.paint(cr)
        Gdk.Cairo.restore(cr)

    def get_type(self):
        pass

    def item_add(self, widget):
        pass

    def item_remove(self, widget):
        pass

    def item_set_expand(self, widget: Gtk.Widget, expand):
        pass

    def item_set_fill(self, child, fill):
        pass

    def item_set_packing(self, child, pack_type):
        pass

    def set_label(self, label):
        pass

    def get_socket_radius(self):
        pass

    def set_socket_radius(self, radius):
        pass

    def get_expanded(self):
        pass

    def set_expanded(self, expanded):
        pass

    def block_expander(self):
        pass

    def unblock_expander(self):
        pass

    def get_sinks(self):
        pass

    def get_sources(self):
        pass

    def export_properties(self):
        pass

    def set_icon_name(self, icon_name):
        pass
