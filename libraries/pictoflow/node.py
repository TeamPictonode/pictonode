# GNU AGPL v3 License
# Written by Stephen Foster and John Nunley, derived from code by Armin Luntzer and AliensGroup

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
gi.require_foreign("cairo")
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject
import cairo
# autopep8: on

CLICKED_TIMEOUT = 250

class SocketIO(Enum):
  DISABLE = 0
  SINK = 1
  SOURCE = 2

class _NodeChild:
    item: Gtk.Widget
    socket: Gtk.Widget

    input_id: int


class Node(Gtk.Box):
    __event_window: Union[Gdk.Window, NoneType]
    __children: List[_NodeChild]

    id = GObject.Property(type=int, default=0)
    x = GObject.Property(type=int, default=0)
    y = GObject.Property(type=int, default=0)
    width = GObject.Property(type=int, default=0)
    height = GObject.Property(type=int, default=0)
    socketid = GObject.Property(type=int, default=0)
    inputid = GObject.Property(type=int, default=0)

    __socket_radius: float
    __func_x: int
    __func_y: int
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

    __alloc_x: int
    __alloc_y: int
    __alloc_width: int
    __alloc_height: int

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

        self.__func_x = 0
        self.__func_y = 0
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

        self.__alloc_x = 0
        self.__alloc_y = 0
        self.__alloc_width = 0
        self.__alloc_height = 0

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

        # Cancel activate_id, which is a timeout from gdk threads
        if self.__activate_id is not None:
            GObject.source_remove(self.__activate_id)
            self.__activate_id = None

        super().do_unrealize()

    def do_adjust_size_request(self, orientation: Gtk.Orientation, minimum: int, natural: int):
        print("Adjust size request, no known way of doing this using Python alone")

    def do_size_allocate(self, allocation: Gdk.Allocation):
        self.__alloc_x = allocation.x
        self.__alloc_y = allocation.y
        self.__alloc_width = allocation.width
        self.__alloc_height = allocation.height

        top = self.__padding_top + self.__margin_top
        bottom = self.__padding_bottom + self.__margin_bottom
        left = self.__padding_left + self.__margin_left
        right = self.__padding_right + self.__margin_right

        allocation.x = left
        allocation.y = top
        allocation.width -= left + right
        allocation.height -= top + bottom

        super().do_size_allocate(allocation)

        if self.__expander.get_expanded():
            expander_alloc = self.__expander.get_allocation()
            minimum, natural = self.__expander.get_preferred_width()
            expander_alloc.width = min(natural, minimum)
            self.__expander.set_allocation(expander_alloc)

            self.__alloc_width = expander_alloc.width + left + right + 25
            expander_alloc.y = 0

            # TODO: Allocate visible sockets
            self.__alloc_height = expander_alloc.height
        else:
            # TODO: Allocate visible child sockets
            pass

        self.set_allocation(allocation)

        if not self.get_realized():
            return

        if self.__event_window is not None:
            return

        self.__event_window.move_resize(
            allocation.x, allocation.y, allocation.width, allocation.height)

    def do_draw(self, cr: cairo.Context):
        print("node - do draw")
        allocation = self.get_allocation()
        allocation.x = self.margin_left
        allocation.y = self.margin_top
        allocation.width -= self.margin_left + self.margin_right
        allocation.height -= self.margin_top + self.margin_bottom

        self.draw_frame(cr, allocation)
        super().draw(cr)

        return Gdk.EVENT_PROPAGATE

    def do_button_press(self, event: Gdk.EventButton):
        point = Gdk.Rectangle()
        point.x = event.x
        point.y = event.y
        point.width = 1
        point.height = 1

        rectangle_func = Gdk.Rectangle()
        rectangle_func.x = self.__func_x
        rectangle_func.width = self.__func_width
        rectangle_func.height = self.__func_height

        # See if these two rectangles intersect
        if not Gdk.Rectangle.intersect(rectangle_func, point, None):
            return False

        self.__activate_id = Gdk.threads_add_timeout(
            CLICKED_TIMEOUT,
            self.__on_clicked_timeout
        )

        return True

    def do_button_release(self, event: Gdk.EventButton):
        if self.__activate_id is not None:
            # Emit the node-func-clicked signal
            self.emit("node-func-clicked", self)

        return True

    def do_add(self, child: Gtk.Widget):
        self.__do_add_real(child, SocketIO.SOURCE)

    def do_remove(self, child: Gtk.Widget):
        for i, c in enumerate(self.__children):
            if c.item != child:
                continue

            self.__children.pop(i)
            c.socket.unparent()
            super().remove(child)
            return

    def do_forall(self, internal: bool, callback: Gtk.Callback, user_data: object):
        super().do_forall(internal, callback, user_data)

        if not internal:
            return

        for child in self.__children:
            callback(child.socket, user_data)

    def do_set_child_property(self, child: Gtk.Widget, property_id: int, value: object, pspec: GObject.ParamSpec):
        # TODO
        pass

    def do_get_child_property(self, child: Gtk.Widget, property_id: int, value: object, pspec: GObject.ParamSpec):
        # TODO
        pass

    def __get_child(self, child: Gtk.Widget) -> Union[_NodeChild, NoneType]:
        for c in self.__children:
            if c.item == child:
                return c

        return None

    def __socket_drag_begin(self, widget: Gtk.Widget):
        alloc_node = self.get_allocation()
        alloc_socket = widget.get_allocation()

        self.emit(
            "node-drag-begin",
            alloc_node.x + alloc_socket.x + alloc_socket.width / 2,
            alloc_node.y + alloc_socket.y + alloc_socket.height / 2
        )

    def __socket_drag_end(self, widget: Gtk.Widget):
        self.emit("node-drag-end")

    def __connect_cb(self, source: Gtk.Widget, target: Gtk.Widget):
        self.emit("node-connect", source, target)

    def __disconnect_cb(self, source: Gtk.Widget, target: Gtk.Widget):
        self.emit("node-disconnect", source, target)

    def __socket_destroyed(self, socket: Gtk.Widget):
        self.emit("node-socket-destroyed", socket)

    def __expander_cb(self, expander: Gtk.Expander, param_spec: GObject.ParamSpec):
        exp = self.__expander.get_expanded()

        for child in self.__children:
            child.socket.set_visible(exp)

        center = self.get_center_widget()
        if center is not None:
            center.set_visible(exp)
        
        self.get_parent().queue_draw()

    def __do_add_real(self, child: Gtk.Widget, io: SocketIO):
        child_info = _NodeChild()

        # TODO: Create a socket

        if self.__event_window:
            child_info.item.set_parent_window(self.__event_window)
            child_info.socket.set_parent_window(self.__event_window)
        
        # TODO: Set socket ID/radius

        child_info.socket.connect("socket-drag-begin", self.__socket_drag_begin)
        child_info.socket.connect("socket-drag-end", self.__socket_drag_end)
        child_info.socket.connect("socket-connect", self.__connect_cb)
        child_info.socket.connect("socket-disconnect", self.__disconnect_cb)
        child_info.socket.connect("destroy", self.__socket_destroyed)

        self.__children.append(child_info)

        self.pack_start(child_info.socket, False, False, 0)
        child_info.socket.set_parent(self)
        child_info.socket.set_visible(True)

    def draw_frame(self, cr: cairo.Context, allocation: Gdk.Allocation):
        # TODO
        pass

        '''
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
        '''

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
