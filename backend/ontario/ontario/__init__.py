# GNU AGPL v3 License
# Written by John Nunley

# autopep8 off
from typing import List
import gi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
# autopep8 on


Gegl.init([])


class ImageContext:
    """
    The overarching context for an image builder.
    """

    # The underlying parent node
    _parent: Gegl.Node

    def __init__(self):
        self._parent = Gegl.Node()


class ImageBuilder:
    """
    A composable interface monad for creating images.
    """

    # The underlying GEGL nodes.
    __nodes: List[Gegl.Node]

    # The parent node.
    __parent: Gegl.Node

    def __init__(self, context: ImageContext):
        self.__nodes = []
        self.__parent = context._parent

    def load_from_file(self, path: str) -> "ImageBuilder":
        """
        Loads an image from a file.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:load")
        node.set_property("path", path)
        self.__parent.add_child(node)
        self.__nodes.append(node)
        return self

    def save_to_file(self, path: str) -> "ImageBuilder":
        """
        Saves an image to a file.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:save")
        node.set_property("path", path)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def load_from_buffer(self, buffer: Gegl.Buffer) -> "ImageBuilder":
        """
        Loads an image from a buffer.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:buffer-source")
        node.set_property("buffer", buffer)
        self.__parent.add_child(node)
        self.__nodes.append(node)
        return self

    def save_to_buffer(self) -> Gegl.Buffer:
        """
        Saves an image to a buffer.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:buffer-source")
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return node.get_property("buffer")

    def composite(self, other: "ImageBuilder") -> "ImageBuilder":
        """
        Composites two images.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:over")
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "aux")
        other.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def invert(self) -> "ImageBuilder":
        """
        Inverts an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:invert")
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def crop(self, x: int, y: int, width: int, height: int) -> "ImageBuilder":
        """
        Crops an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:crop")
        node.set_property("x", x)
        node.set_property("y", y)
        node.set_property("width", width)
        node.set_property("height", height)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def flip(self, horizontal: bool, vertical: bool) -> "ImageBuilder":
        """
        Flips an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:flip")
        node.set_property("horizontal", horizontal)
        node.set_property("vertical", vertical)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def rotate(self, angle: float) -> "ImageBuilder":
        """
        Rotates an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:rotate")
        node.set_property("angle", angle)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def resize(self, width: int, height: int) -> "ImageBuilder":
        """
        Resizes an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:resize")
        node.set_property("width", width)
        node.set_property("height", height)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def color_balance(self, cyan_red: float, magenta_green: float, yellow_blue: float) -> "ImageBuilder":
        """
        Color balances an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:color-balance")
        node.set_property("cyan-red", cyan_red)
        node.set_property("magenta-green", magenta_green)
        node.set_property("yellow-blue", yellow_blue)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def brightness_contrast(self, brightness: float, contrast: float) -> "ImageBuilder":
        """
        Brightness and contrast an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:brightness-contrast")
        node.set_property("brightness", brightness)
        node.set_property("contrast", contrast)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def hue_saturation(self, hue: float, saturation: float) -> "ImageBuilder":
        """
        Hue and saturation an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:hue-saturation")
        node.set_property("hue", hue)
        node.set_property("saturation", saturation)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def curves(self, curve: str) -> "ImageBuilder":
        """
        Curves an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:curves")
        node.set_property("curve", curve)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def unsharp_mask(self, radius: float, amount: float) -> "ImageBuilder":
        """
        Unsharp masks an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:unsharp-mask")
        node.set_property("radius", radius)
        node.set_property("amount", amount)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def gaussian_blur(self, radius: float) -> "ImageBuilder":
        """
        Gaussian blurs an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:gaussian-blur")
        node.set_property("radius", radius)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def perspective_transform(self, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> "ImageBuilder":
        """
        Perspective transforms an image.
        """

        node = Gegl.Node()
        node.set_property("operation", "gegl:perspective-transform")
        node.set_property("x0", x0)
        node.set_property("y0", y0)
        node.set_property("x1", x1)
        node.set_property("y1", y1)
        node.set_property("x2", x2)
        node.set_property("y2", y2)
        node.set_property("x3", x3)
        node.set_property("y3", y3)
        self.__parent.add_child(node)

        # Connect the last node to the save node.
        self.__nodes[-1].connect_to("output", node, "input")

        self.__nodes.append(node)
        return self

    def process(self):
        """
        Processes the image.
        """

        self.__nodes[-1].process()
