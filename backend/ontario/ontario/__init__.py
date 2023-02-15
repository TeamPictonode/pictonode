# GNU AGPL v3 License
# Written by John Nunley and Parker Nelms

# autopep8 off
from typing import List
from gi.repository import Gegl
import gi
gi.require_version('Gegl', '0.4')
import os
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

    def reset_context(self):
        for child in self._parent.get_children():
            self._parent.remove_child(child)


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
        Loads an image file to create a source node.
        Currently only supports .png, .jpg, and .exr
        """

        # get file extention
        split_ext: tuple = os.path.splitext(path)
        file_ext: str = split_ext[-1]
        file_ext = file_ext.lower()

        # add node as a child to the image context
        if file_ext == '.png':
            node = self._parent.create_child("gegl:png-load")
        
        elif file_ext == '.jpg' or file_ext == '.jpeg':
            node = self._parent.create_child("gegl:jpg-load")

        elif file_ext == '.exr':
            node = self._parent.create_child("gegl:exr-load")

        elif file_ext == '.svg':
            # TODO
            pass

        # add node to node list
        self.__nodes.append(node)
        return self

    def load_from_buffer(self, buffer: Gegl.Buffer) -> "ImageBuilder":
        """
        Loads a buffer to create a source node.
        """

        # create new source buffer node
        node = self.__parent.create_child("gegl:gegl-load")
        node.set_property("buffer", buffer)

        # add node to node list
        self.__nodes.append(node)
        return self

    def save_to_file(self, path: str) -> "ImageBuilder":
        """
        Saves an image of arbitrary type to a file.
        """

        # create generic image save node (uses different save handlers,
        # depending on file type)
        node = self.__parent.create_child("gegl:save")
        node.set_property("path", path)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

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
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return node.get_property("buffer")

    def composite(self, other: "ImageBuilder") -> "ImageBuilder":
        """
        Composites two images.
        """

        # TODO: implement gegl:layer operation
        return self

    def invert(self) -> "ImageBuilder":
        """
        Inverts an image.
        """

        # create child node invert
        node = self.__parent.create_child("gegl:invert")

        # Connect the last node to the new node.
        self.__nodes[-1].link(node)

        # add new node to node list
        self.__nodes.append(node)
        return self

    def crop(self, x: int, y: int, width: int, height: int) -> "ImageBuilder":
        """
        Crops an image.
        """

        node = self.__parent.create_child("gegl:crop")
        node.set_property("x", x)
        node.set_property("y", y)
        node.set_property("width", width)
        node.set_property("height", height)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def flip(self, horizontal: bool, vertical: bool) -> "ImageBuilder":
        """
        Flips an image.
        """

        # TODO: need to implement transform operations, namely "gegl:reflect"

        return self

    def rotate(self, origin_x: float, origin_y: float, degrees: float) -> "ImageBuilder":
        """
        Rotates an image.
        """

        node = self.__parent.create_child("gegl:rotate")
        node.set_property("origin-x", origin_x)
        node.set_property("origin-y", origin_x)
        node.set_property("degrees", degrees)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def resize(self, width: float, height: float) -> "ImageBuilder":
        """
        Resizes an image.
        """

        node = self.__parent.create_child("gegl:scale-sizes")
        node.set_property("x", width)
        node.set_property("y", height)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def color_balance(self, cyan_red: float, magenta_green: float, yellow_blue: float) -> "ImageBuilder":
        """
        Color balances an image.
        """

        # TODO: need to implement a few different operation, namely "gegl:component-extract"
        # to separate channels and then compositing to combine. May need to be done in the gtk node side

        return self

    def brightness_contrast(self, brightness: float, contrast: float) -> "ImageBuilder":
        """
        Brightness and contrast an image.

        Note: -5 <= Contrast <= 5
        Note: -3 <= Brightness <= 3
        """

        node = self.__parent.create_child("gegl:brightness-contrast")
        node.set_property("contrast", contrast)
        node.set_property("brightness", brightness)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def hue_chroma_lightness(self, hue: float, chroma: float, lightness: float) -> "ImageBuilder":
        """
        Hue, chroma, and lightness an image.
        """

        node = self.__parent.creat_child("gegl:hue-chroma")
        node.set_property("hue", hue)
        node.set_property("chroma", chroma)
        node.set_property("lightness", lightness)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def curves(self, curve: str) -> "ImageBuilder":
        """
        Curves an image.
        """

        # TODO: once again will have to use something like "gegl:contrast-curve" and component extraction
        return self

    def unsharp_mask(self, radius: float, amount: float) -> "ImageBuilder":
        """
        Unsharp masks an image.
        """

        node = self.__parent.create_child("gegl:unsharp-mask")
        node.set_property("std-dev", radius)
        node.set_property("scale", amount)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def gaussian_blur(self, x: float, y: float) -> "ImageBuilder":
        """
        Gaussian blurs an image.
        """

        node = self.__parent.create_child("gegl:gaussian-blur")
        node.set_property("std-dev-x", x)
        node.set_property("std-dev-y", y)

        # Connect the last node to the save node.
        self.__nodes[-1].link(node)

        self.__nodes.append(node)
        return self

    def perspective_transform(self, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> "ImageBuilder":
        """
        Perspective transforms an image.
        """

        # TODO: involves the use of several transform operations.
        return self

    def process(self):
        """
        Processes the image.
        """

        self.__nodes[-1].process()
