import sys
from gi.repository import Gegl as gegl

try:
    origin, target = sys.argv[1:3]
except IndexError:
    sys.stderr.write("Usage: %s origin_png target_png" % __file__)
    sys.exit(1)

gegl.init([])

ops = gegl.list_operations()

x = gegl.Node()

y = gegl.Node()
y.set_property("operation", "gegl:jpg-load")
y.set_property("path", origin)
x.add_child(y)

z = gegl.Node()
z.set_property("operation", "gegl:invert")
x.add_child(z)

w = gegl.Node()
w.set_property("operation", "gegl:jpg-save")
w.set_property("path", target)
x.add_child(w)

y.connect_to("output",z,"input")
z.connect_to("output", w, "input")

w.process()