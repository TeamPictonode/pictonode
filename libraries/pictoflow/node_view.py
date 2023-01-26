# GNU AGPL v3 License
# Written by Stephen Foster and John Nunley, derived from code by aluntzer and AliensGroup

import cairo
import os
import sys

from enum import Enum
from typing import Union
from types import NoneType

from collections.abc import List

if sys.platform == "win32":
    os.environ['GI_TYPELIB_PATH'] = "C:\Program Files\GIMP %GIMP_VERSION%\lib\girepository-1.0"

# autopep8: off
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_foreign('cairo')

from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk
# autopep8: on


RESIZE_RECTANGLE = 16


class _Action(Enum):
    NONE = 0
    DRAG_CHILD = 1
    DRAG_CONNECTION = 2
    RESIZE_CHILD = 3


class _NodeViewChild:
    widget: Gtk.Widget
    rectangle: Gdk.Rectangle
    south_east: Gdk.Rectangle

    start_x: int
    start_y: int
    dx: int
    dy: int


class _NodeViewConnection:
    source: Gtk.Widget
    target: Gtk.Widget


def connecting_curve(cr: cairo.Context, x0: int, y0: int, x1: int, y1: int):
    cr.move_to(x0, y0)

    d = abs(x1 - x0) / 2

    x1m = x0 + d
    y1m = y0

    x2m = x1 - d
    y2m = y1

    cr.curve_to(x1m, y1m, x2m, y2m, x1, y1)


def point_in_rect(rect: Gdk.Rectangle, x: int, y: int):
    pt = Gdk.Rectangle()
    pt.x = x
    pt.y = y
    pt.width = 1
    pt.height = 1

    return Gdk.Rectangle.intersect(rect, pt, None)


class NodeView(Gtk.Container):
    __gtype_name__ = "NodeView"

    event_window: Union[Gdk.Window, NoneType]
    children: List[_NodeViewChild]
    connections: List[_NodeViewConnection]
    action: _Action
    node_id: Union[int, NoneType]

    action_x0: int
    action_y0: int
    action_x1: int
    action_y1: int

    default_cursor: Union[Gdk.Cursor, NoneType]
    se_resize_cursor: Union[Gdk.Cursor, NoneType]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.children = []
        self.connections = []
        self.action = _Action.NONE
        self.node_id = None
        self.event_window = None
        self.set_has_window(False)
        self.set_size_request(100, 100)

        self.action_x0 = 0
        self.action_y0 = 0
        self.action_x1 = 0
        self.action_y1 = 0

        self.__cursor_init()
        self.drag_dest_set(Gtk.DestDefaults.MOTION, [], Gdk.DragAction.PRIVATE)
        self.drag_dest_set_track_motion(True)
        self.connect("drag-motion", self.__drag_motion)

    def do_map(self):
        self.set_mapped(True)

        for child in self.children:
            if not child.widget.get_visible():
                continue

            if not child.widget.get_mapped():
                child.widget.map()

        if self.event_window is not None:
            self.event_window.show()

    def do_unmap(self):
        if self.event_window is not None:
            self.event_window.hide()

        super().do_unmap()

    def do_realize(self):
        self.set_realized(True)

        allocation = self.get_allocation()

        # Set up attributes for the event window
        attributes = Gdk.WindowAttr()
        attributes.window_type = Gdk.WindowType.CHILD
        attributes.x = allocation.x
        attributes.y = allocation.y
        attributes.width = allocation.width
        attributes.height = allocation.height
        attributes.wclass = Gdk.WindowWindowClass.INPUT_OUTPUT
        attributes.event_mask = self.get_events()
        attributes |= (Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK |
                       Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.TOUCH_MASK | Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)

        attributes_mask = Gdk.WindowAttributesType.X | Gdk.WindowAttributesType.Y

        window = self.get_parent_window()
        self.set_widow(window)

        self.event_window = Gdk.Window.new(window, attributes, attributes_mask)
        self.register_window(self.event_window)

        for child in self.children:
            child.widget.set_parent_window(self.event_window)

    def do_unrealize(self):
        if self.event_window is not None:
            self.unregister_window(self.event_window)
            self.event_window.destroy()
            self.event_window = None

        super().do_unrealize()

    def do_size_allocate(self, allocation):
        for child in self.children:
            requisition = child.widget.get_preferred_size(None)
            child.rectangle.x = child.get_property("x")
            child.rectangle.y = child.get_property("y")

            allocation_child = Gdk.Allocation()
            allocation_child.x = child.rectangle.x
            allocation_child.y = child.rectangle.y
            allocation_child.width = max(
                requisition.width, child.rectangle.width)
            allocation_child.height = max(
                requisition.height, child.rectangle.height)

            child.widget.size_allocate(allocation_child)
            allocation_child = child.widget.get_allocation()

            # TODO: IsNode function for socket radius
            socket_radius = 0

            child.south_east.x = allocation_child.width - socket_radius - RESIZE_RECTANGLE
            child.south_east.y = allocation_child.height - socket_radius - RESIZE_RECTANGLE

            w = allocation_child.x + allocation_child.width
            h = allocation_child.y + allocation_child.height

            if w > allocation.width:
                allocation.width = w
            if h > allocation.height:
                allocation.height = h

        self.set_allocation(allocation)
        self.set_size_request(allocation.width, allocation.height)

        if not self.get_realized():
            return

        if not self.event_window:
            return

        self.event_window.move_resize(
            allocation.x, allocation.y, allocation.width, allocation.height)

    def do_draw(self, cr: cairo.Context):
        if self.action == _Action.DRAG_CONNECTION:
            cr.save()
            cr.set_source_rgba(1.0, 0.2, 0.2, 0.6)

            connecting_curve(cr, self.action_x0, self.action_y0,
                             self.action_x1, self.action_y1)
            cr.stroke()
            cr.restore()

        for conn in self.connections:
            self.__draw_socket_connection(cr, conn)

        if Gtk.cairo_should_draw_window(cr, self.event_window):
            super().do_draw(cr)

        return Gdk.EVENT_PROPAGATE

    def do_add(self, widget: Gtk.Widget):
        child = _NodeViewChild(widget)
        child.rectangle.x = 100
        child.rectangle.y = 100
        child.rectangle.width = 100
        child.rectangle.height = 100

        child.south_east.x = child.rectangle.width - RESIZE_RECTANGLE
        child.south_east.y = child.rectangle.height - RESIZE_RECTANGLE
        child.south_east.width = RESIZE_RECTANGLE
        child.south_east.height = RESIZE_RECTANGLE

        widget.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.BUTTON1_MOTION_MASK
        )

        # Connect all of the signals.
        widget.connect("button-press-event", self.__child_button_press, child)
        widget.connect("button-release-event",
                       self.__child_button_release, child)
        widget.connect("motion-notify-event",
                       self.__child_motion_notify, child)
        widget.connect("leave-notify-event", self.__child_pointer_crossing)

        # TODO: Test to see if the child is a widget
        if True:
            widget.connect("node-drag-begin", self.__drag_begin)
            widget.connect("node-drag-end", self.__drag_end)
            widget.connect("node-socket-connect", self.__socket_connect)
            widget.connect("node-socket-disconnect", self.__socket_disconnect)
            widget.connect("node-socket-destroyed", self.__socket_destroyed)

            # Set the node ID.
            node_id = self.node_id
            self.node_id += 1
            widget.set_property("id", node_id)

        self.children.append(child)

        if self.get_realized():
            widget.set_parent_window(self.event_window)

        widget.set_parent(self)
        widget.show_all()

    def do_remove(self, widget: Gtk.Widget):
        child = self.__get_child(widget)
        self.children.remove(child)

        widget.unparent()

    def do_forall(self, include_internals: bool, callback, *callback_parameters):
        print("do_forall() self = %x" % id(self))

        if not callback is None:
            for child in self.children:
                callback(child.widget, *callback_parameters)

    def do_child_type(self):
        print("do_child_type()")

        # TODO: Return the type of the child node

        return (Gtk.Widget.get_type())

    def __child_motion_notify(self, w: Gtk.Widget, event: Gdk.EventMotion, child: _NodeViewChild):
        if self.action == _Action.NONE:
            inside = point_in_rect(child.south_east, event.x, event.y)

            if inside:
                self.__cursor_set(_Action.RESIZE_CHILD)
            else:
                self.__cursor_set(_Action.NONE)

        if event.state & Gdk.ModifierType.BUTTON1_MASK != 0:
            if self.action == _Action.DRAG_CHILD:
                # TODO: block expander/move child
                self.__move_child(
                    child,
                    event.x - child.start_x,
                    event.y - child.start_y
                )
            elif self.action == _Action.RESIZE_CHILD:
                w = event.x - child.rectangle.x - child.dx
                h = event.y - child.rectangle.y - child.dy

                child.widget.set_property("width", w)
                child.widget.set_property("height", h)

                child.widget.queue_resize()
                self.queue_draw()

        return Gdk.EVENT_LAST

    def __child_pointer_crossing(self, w: Gtk.Widget, event: Gdk.EventCrossing):
        if self.action == _Action.RESIZE_CHILD:
            return Gdk.EVENT_PROPAGATE

        if event.type == Gdk.EventType.LEAVE_NOTIFY:
            self.__cursor_set(_Action.NONE)

        return Gdk.EVENT_PROPAGATE

    def __child_button_press(self, w: Gtk.Widget, event: Gdk.EventButton, child: _NodeViewChild):
        if event.button == Gdk.BUTTON_PRIMARY:
            inside = point_in_rect(child.south_east, event.x, event.y)

            if inside:
                self.action = _Action.RESIZE_CHILD
            else:
                self.action = _Action.DRAG_CHILD

            child.start_x = event.x
            child.start_y = event.y

            child_alloc = child.widget.get_allocation()
            child.dx = event.x - (child_alloc.x + child_alloc.width)
            child.dy = event.y - (child_alloc.y + child_alloc.height)

        return Gdk.EVENT_PROPAGATE

    def __child_button_release(self, w: Gtk.Widget, event: Gdk.EventButton, child: _NodeViewChild):
        if event.button == Gdk.BUTTON_PRIMARY:
            # TODO: unblock
            pass

        self.action = _Action.NONE

        self.children.remove(child)
        self.children.append(child)
        self.queue_draw()

        return Gdk.EVENT_PROPAGATE

    def __drag_begin(self, w: Gtk.Widget, x0: int, y0: int):
        self.action = _Action.DRAG_CONNECTION
        self.action_x0 = x0
        self.action_y0 = y0

        return Gdk.EVENT_PROPAGATE

    def __drag_end(self, w: Gtk.Widget):
        self.action = _Action.NONE
        self.queue_draw()

        return Gdk.EVENT_PROPAGATE

    def __socket_connect(self, w: Gtk.Widget, source: Gtk.Widget, sink: Gtk.Widget):
        conn = _NodeViewConnection(source, sink)
        self.connections.append(conn)
        self.queue_draw()

        return Gdk.EVENT_PROPAGATE

    def __socket_disconnect(self, w: Gtk.Widget, source: Gtk.Widget, sink: Gtk.Widget):
        for conn in self.connections:
            if conn.source == source and conn.sink == sink:
                self.connections.remove(conn)
                self.queue_draw()
                break

        return Gdk.EVENT_PROPAGATE

    def __socket_destroyed(self, w: Gtk.Widget, socket: Gtk.Widget):
        for conn in self.connections:
            if conn.source == socket or conn.sink == socket:
                self.connections.remove(conn)
                self.queue_draw()
                break

        return Gdk.EVENT_PROPAGATE

    def __move_child(self, child: _NodeViewChild, x: int, y: int):
        view_alloc = self.get_allocation()
        node_alloc = child.widget.get_allocation()

        x = child.rectangle.x + x
        y = child.rectangle.y + y

        xmax = view_alloc.width - node_alloc.width
        ymax = view_alloc.height - node_alloc.height

        if x > 0 and x < xmax:
            child.rectangle.x = x
        elif x < 0:
            child.rectangle.x = 0
        else:
            child.rectangle.x = xmax

        if y > 0 and y < ymax:
            child.rectangle.y = y
        elif y < 0:
            child.rectangle.y = 0
        else:
            child.rectangle.y = ymax

        child.widget.set("x", child.rectangle.x)
        child.widget.set("y", child.rectangle.y)

        self.children.remove(child)
        self.children.append(child)

        self.queue_draw()

    def __get_child(self, widget: Gtk.Widget) -> Union[_NodeViewChild, NoneType]:
        for child in self.children:
            if child.widget == widget:
                return child

        return None

    def __cursor_init(self):
        display = self.get_display()
        self.default_cursor = Gdk.Cursor.new_from_name(display, "default")
        self.se_resize_cursor = Gdk.Cursor.new_from_name(display, "se-resize")

    def __cursor_set(self, action: _Action):
        window = self.get_window()

        if action == _Action.RESIZE_CHILD:
            window.set_cursor(self.se_resize_cursor)
        else:
            window.set_cursor(self.default_cursor)

    def __drag_motion(self, w: Gtk.Widget, x: int, y: int, time: int):
        self.queue_draw()
        return Gdk.EVENT_PROPAGATE

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
                self.get_window().move_resize(allocation.x, allocation.y,
                                              allocation.width, allocation.height)

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

    def do_set_child_property(self, child: Gtk.Widget, property_id: int, value: GObject.Value, pspec: GObject.ParamSpec):
        print("do_set_child_property()")
        # TODO

    def do_get_child_property(self, child: Gtk.Widget, property_id: int, value: GObject.Value, pspec: GObject.ParamSpec):
        print("do_get_child_property()")
        # TODO

    def __draw_socket_connection(self, cr: cairo.Context, conn: _NodeViewConnection):
        def x_and_y_for(widget: Gtk.Widget):
            parent_alloc = widget.get_parent().get_allocation()
            alloc = widget.get_allocation()

            x0 = alloc.x + (alloc.width / 2) + parent_alloc.x
            y0 = alloc.y + (alloc.height / 2) + parent_alloc.y

            return x0, y0

        x0, y0 = x_and_y_for(conn.source)
        x1, y1 = x_and_y_for(conn.target)
        pat = cairo.LinearGradient(x0, y0, x1, y1)

        # TODO: RGBA
        rgba1 = Gdk.RGBA()
        rgba1.red = 0.0
        rgba1.green = 0.0
        rgba1.blue = 0.0
        rgba1.alpha = 1.0

        rgba2 = Gdk.RGBA()
        rgba2.red = 0.0
        rgba2.green = 0.0
        rgba2.blue = 1.0
        rgba2.alpha = 1.0

        # Add color stops to the pattern.
        pat.add_color_stop_rgba(
            0.0, rgba1.red, rgba1.green, rgba1.blue, rgba1.alpha)
        pat.add_color_stop_rgba(
            1.0, rgba2.red, rgba2.green, rgba2.blue, rgba2.alpha)

        cr.save()

        connecting_curve(cr, x0, y0, x1, y1)
        cr.set_source(pat)
        cr.stroke()

        cr.restore()
