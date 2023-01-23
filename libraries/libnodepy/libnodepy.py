# GNU AGPL v3 License
# Written by John Nunley

from abc import ABC, abstractmethod
from collections.abc import List, Dict
from typing import TypeVar, Generic, Callable, Optional, Any, Union

MAX_NODES = 1 << 24

T = TypeVar('T')
M = TypeVar('M')

class __HydrateTarget(ABC):
  """
  A target for hydrating a node.
  """

  @abstractmethod
  def isNoNode(self) -> bool:
    """
    Returns whether or not the target is a NoNode.
    """

    pass

  @abstractmethod
  def hydrate(self):
    """
    Hydrates a node.
    """

    pass

class __NoNode(__HydrateTarget):
  """
  A stand-in for a node that doesn't exist.
  """
  
  def __init__(self):
    pass

  def isNoNode(self) -> bool:
    return False

  def hydrate(self):
    pass

class LinkTemplate(Generic[T, M]):
  """
  A template for creating a link.
  """

  # Metadata for the link.
  __metadata: M

  # Default value for the link.
  __defaultValue: T

  def __init__(self, metadata: M, defaultValue: T):
    self.__metadata = metadata
    self.__defaultValue = defaultValue

  def getMetadata(self) -> M:
    """
    Returns the metadata for the link.
    """

    return self.__metadata

  def getDefaultValue(self) -> T:
    """
    Returns the default value for the link.
    """

    return self.__defaultValue

class Link(Generic[T, M]):
  """
  A link between two nodes.
  """

  # The template for the link.
  __template: LinkTemplate[T, M]

  # The ID number of the link.
  __id: int

  # The node this link is coming from.
  __from: __HydrateTarget

  # The node this link is going to.
  __to: __HydrateTarget

  # The index of the link in the from node.
  __fromIndex: int

  # The index of the link in the to node.
  __toIndex: int

  # The metadata for the link.
  __metadata: M

  # The value of the link.
  __value: T

  # Whether or not the link needs to be hydrated.
  __dirty: bool

  # Is the link using a custom value?
  __customDefault: bool

  def __init__(self, template: LinkTemplate[T, M], metadata: M, id: int):
    self.__template = template
    self.__id = id
    self.__from = __NoNode()
    self.__to = __NoNode()
    self.__fromIndex = -1
    self.__toIndex = -1
    self.__metadata = metadata
    self.__value = template.getDefaultValue()
    self.__dirty = True
    self.__customDefault = False

  def getId(self) -> int:
    """
    Returns the ID number of the link.
    """

    return self.__id

  def setId(self, id: int):
    self.__id = id

  def setMetadata(self, metadata: M):
    self.__metadata = metadata

  def isFromOccupied(self) -> bool:
    return not self.__from.isNoNode()

  def isToOccupied(self) -> bool:
    return not self.__to.isNoNode()

  def setFrom(self, node: __HydrateTarget, index: int):
    self.__from = node
    self.__fromIndex = index

  def setTo(self, node: __HydrateTarget, index: int):
    self.__to = node
    self.__toIndex = index
  
  def clearFrom(self):
    self.__from = __NoNode()
    self.__fromIndex = -1

  def clearTo(self):
    self.__to = __NoNode()
    self.__toIndex = -1

  def isDirty(self):
    """
    Is the link dirty?
    """
    
    return self.__dirty

  def hydrate(self):
    """
    Hydrates the link.
    """

    self.__from.hydrate()
    self.__to.hydrate()

  def getValue(self) -> T:
    """
    Returns the value of the link.
    """

    self.hydrate()
    return self.__value

  def setValue(self, value: T):
    """
    Sets the value of the link.
    """

    self.__value = value
    self.__customDefault = True
    self.__dirty = True

  def getFromIndex(self) -> int:
    """
    Returns the index of the link in the from node.
    """

    return self.__fromIndex

  def getToIndex(self) -> int:
    """
    Returns the index of the link in the to node.
    """

    return self.__toIndex

  def getMetadata(self) -> M:
    """
    Returns the metadata for the link.
    """

    return self.__metadata

class NodeTemplate(Generic[T, M]):
  """
  A template for creating a node.
  """

  # Callback to call when the data is processed.
  __onProcess: Callable[[List[Link[T, M]]], List[T]]

  # Input link templates.
  __inputs: List[LinkTemplate[T, M]]

  # Output link templates.
  __outputs: List[LinkTemplate[T, M]]

  # Metadata for the node.
  __metadata: M

  def __init__(
    self,
    onProcess: Callable[[List[Link[T, M]]], List[T]],
    inputs: List[LinkTemplate[T, M]],
    outputs: List[LinkTemplate[T, M]],
    metadata: M
  ):
    self.__onProcess = onProcess
    self.__inputs = inputs
    self.__outputs = outputs
    self.__metadata = metadata

  def getMetadata(self) -> M:
    """
    Returns the metadata for the node.
    """

    return self.__metadata

  def getInputs(self) -> List[LinkTemplate[T, M]]:
    """
    Returns the input link templates.
    """

    return self.__inputs

  def getOutputs(self) -> List[LinkTemplate[T, M]]:
    """
    Returns the output link templates.
    """

    return self.__outputs

  def process(self, inputs: List[Link[T, M]]) -> List[T]:
    """
    Processes the node.

    Probably shouldn't call this unless you know what you're doing.
    """

    return self.__onProcess(inputs)

class TemplateTable(Generic[T, M]):
  """
  A table for node and link templates.
  """

  # The table of node templates.
  __nodeTemplates: Dict[str, NodeTemplate[T, M]]

  def __init__(self):
    self.__nodeTemplates = {}

  def addTemplate(self, name: str, template: NodeTemplate[T, M]):
    """
    Adds a template to the table.
    """

    self.__nodeTemplates[name] = template

  def getTemplate(self, name: str) -> Optional[NodeTemplate[T, M]]:
    """
    Returns a template from the table.
    """

    return self.__nodeTemplates.get(name)

  def getTemplates(self) -> List[str]:
    """
    Returns a list of templates in the table.
    """

    return list(self.__nodeTemplates.keys())

class Node(Generic[T, M], __HydrateTarget):
  """
  A node in the graph.
  """

  # The template table that we're using.
  __templateTable: TemplateTable[T, M]

  # The template for the node.
  __template: str

  # The ID number of the node.
  __id: int

  # The metadata for the node.
  __metadata: M

  # The input links.
  __inputs: List[Link[T, M]]

  # The output links.
  __outputs: List[Link[T, M]]

  def __init__(
    self,
    templateTable: TemplateTable[T, M],
    template: str,
    metadata: M,
    id: int
  ):
    self.__templateTable = templateTable
    self.__template = template
    self.__id = id
    self.__metadata = metadata

    template = templateTable.getTemplate(template)
    lastLinkId = id + MAX_NODES

    self.__inputs = []
    for linkTemplate in template.getInputs():
      self.__inputs.append(
        Link(
          linkTemplate,
          lastLinkId,
          metadata,
        )
      )
      lastLinkId += MAX_NODES

    self.__outputs = []
    for linkTemplate in template.getOutputs():
      self.__outputs.append(
        Link(
          linkTemplate,
          lastLinkId,
          metadata,
        )
      )
      lastLinkId += MAX_NODES

  def getTemplateTable(self) -> TemplateTable[T, M]:
    """
    Returns the template table.
    """

    return self.__templateTable

  def getTemplate(self) -> str:
    """
    Returns the template name.
    """

    return self.__template

  def getId(self) -> int:
    """
    Returns the ID number of the node.
    """

    return self.__id

  def getMetadata(self) -> M:
    """
    Returns the metadata for the node.
    """

    return self.__metadata

  def getInputs(self) -> List[Link[T, M]]:
    """
    Returns the input links.
    """

    return self.__inputs

  def getOutputs(self) -> List[Link[T, M]]:
    """
    Returns the output links.
    """

    return self.__outputs
  
  def _setId(self, id: int):
    """
    (UNSTABLE) Sets the ID number of the node.
    """

    self.__id = id

  def isNoNode(self) -> bool:
    return False

  def hydrate(self):
    # Figure out if we are dirty.
    is_dirty = False
    for link in self.__inputs:
      if link.isDirty():
        is_dirty = True
        break

    # If we are dirty, process the node.
    if not is_dirty:
      return

    # Process the node.
    template = self.__templateTable.getTemplate(self.__template)
    outputs = template.process(self.__inputs)

    # Set the outputs.
    for i in range(len(outputs)):
      self.__outputs[i].setData(outputs[i])

  def _setOutputLink(self, link: Link[T, M], index: int):
    """
    (PRIVATE) Sets the output link.
    """

    self.__outputs[index] = link

  def _replaceLink(self, index: int, input: bool, id: int):
    """
    (PRIVATE) Replaces a link.
    """

    if index < 0:
      return

    template = self.__templateTable.getTemplate(self.__template)

    if input:
      input_template = template.getInputs().get(index)

      if input_template is None:
        raise IndexError("Invalid input index")

      self.__inputs[index] = Link(
        input_template,
        input_template.getMetadata(),
        id,
      )
    else:
      output_template = template.getOutputs().get(index)

      if output_template is None:
        raise IndexError("Invalid output index")

      self.__outputs[index] = Link(
        output_template,
        output_template.getMetadata(),
        id,
      )

  def _linkFrom(
    self,
    from_node: "Node[T, M]",
    from_index: int,
    to_index: int,
    meta: M,
  ) -> Link[T, M]:
    """
    (PRIVATE) Links from another node.
    """

    link = self.__inputs[to_index]
    from_node.__outputs[from_index] = link
    link.__setFrom(from_node, from_index)
    link.__setTo(self, to_index)
    link.__setMetadata(meta)
    return link

  def _unlinkFrom(
    self,
    from_node: "Node[T, M]",
    from_index: int,
    to_index: int,
    id: int,
  ) -> None:
    """
    (PRIVATE) Unlinks from another node.
    """

    from_node._replaceLink(from_index, False, id)
    self.__inputs[to_index].clearFrom()
    self.__inputs[to_index].clearTo()

  def _unlinkAll(self):
    """
    (PRIVATE) Unlinks all links.
    """
    
    for i in range(len(self.__inputs)):
      self.__unlinkFrom(
        self.__inputs[i].getFrom(),
        self.__inputs[i].getFromIndex(),
        i,
        self.__inputs[i].getId(),
      )

    raise NotImplementedError()

  def isInputOccupied(self, index: int) -> bool:
    """
    Returns whether the input is occupied.
    """

    return self.__inputs[index].isFromOccupied()

  def isOutputOccupied(self, index: int) -> bool:
    """
    Returns whether the output is occupied.
    """

    return self.__outputs[index].isToOccupied()

class Pipeline(Generic[T, M]):
  """
  A pipeline consisting of nodes.
  """

  # All nodes in the pipeline.
  __nodes: Dict[int, Node[T, M]]

  # All links in the pipeline.
  __links: Dict[int, Link[T, M]]

  # All templates.
  __templateTable: TemplateTable[T, M]

  # The next ID number.
  __nextId: int

  def __init__(self, templateTable: TemplateTable[T, M]):
    self.__nodes = {}
    self.__links = {}
    self.__templateTable = templateTable
    self.__nextId = 0

  def createNode(self, template: str, metadata: M) -> Node[T, M]:
    """
    Creates a node.
    """
    
    node = Node(self.__templateTable, template, metadata, self.__nextId)
    self.__nodes[self.__nextId] = node
    self.__nextId += MAX_NODES
    return node

  def link(
    self,
    fromId: int,
    fromIndex: int,
    toId: int,
    toIndex: int,
    meta: M,
  ) -> Link[T, M]:
    """
    Link two nodes together and return the link object.
    """

    from_node = self.__nodes[fromId]
    to_node = self.__nodes[toId]

    if from_node.isOutputOccupied(fromIndex):
      raise ValueError("Output is occupied")

    if to_node.isInputOccupied(toIndex):
      raise ValueError("Input is occupied")

    link = to_node._linkFrom(from_node, fromIndex, toIndex, meta)
    self.__links[link.getId()] = link
    return link

  def unlink(
    self,
    fromId: int,
    fromIndex: int,
    toId: int,
    toIndex: int,
  ) -> None:
    """
    Unlink two nodes.
    """
    
    from_node = self.__nodes[fromId]
    to_node = self.__nodes[toId]

    to_node.unlinkFrom(from_node, fromIndex, toIndex)
    self.__nextId += 1

  def getNode(self, id: int) -> Node[T, M]:
    """
    Returns the node with the given ID.
    """

    return self.__nodes[id]

  def getNodes(self) -> List[Node[T, M]]:
    """
    Returns all nodes.
    """

    return list(self.__nodes.values())

SerializedLink = Dict[str, Any]
SerializedNode = Dict[str, Any]
SerializedPipeline = Dict[str, Union[List[SerializedLink], List[SerializedNode]]]

def serializePipeline(pipeline: Pipeline[T, M]) -> SerializedPipeline:
  """
  Serialize a pipeline to a JSON-equivalent dict
  """

  links = []
  nodes = []

  for link in pipeline.__links.values():
    links.append({
      "from": link.getFromId(),
      "fromIndex": link.getFromIndex(),
      "to": link.getToId(),
      "toIndex": link.getToIndex(),
      "metadata": link.getMetadata(),
    })

  for node in pipeline.__nodes.values():
    nodes.append({
      "id": node.getId(),
      "template": node.getTemplate(),
      "metadata": node.getMetadata(),
    })

  return {
    "links": links,
    "nodes": nodes,
  }

def deserializePipeline(
  serialized: SerializedPipeline,
  templateTable: TemplateTable[T, M],
) -> Pipeline[T, M]:
  """
  Deserialize a pipeline from a JSON-equivalent dict
  """

  pipeline = Pipeline(templateTable)

  for serializedNode in serialized["nodes"]:
    node = pipeline.createNode(serializedNode["template"], serializedNode["metadata"])
    node.setId(serializedNode["id"])

  for serializedLink in serialized["links"]:
    pipeline.link(
      serializedLink["from"],
      serializedLink["fromIndex"],
      serializedLink["to"],
      serializedLink["toIndex"],
      serializedLink["metadata"],
    )

  return pipeline
    