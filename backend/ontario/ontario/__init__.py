# GNU AGPL v3 License
# Written by John Nunley

# autopep8 off
import gi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
# autopep8 on

from typing import List

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
