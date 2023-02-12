# GNU AGPL v3 License
# Written by John Nunley

# Parser for the libnode format into gtknodes structures

from . import custom_nodes

import json

TEMPLATE_TABLE = {
    "input": custom_nodes.ImgSrcNode,
    "output": custom_nodes.OutputNode,
}


def parseNodes(nodes: str, root):
    # Parse the nodes as JSON
    nodes = json.loads(nodes)

    id_map = {}

    for node in nodes["nodes"]:
        target_node_class = TEMPLATE_TABLE[node["template"]]
        id = node["id"]

        node = target_node_class()
        root.add(node)
        id_map[id] = node

    for link in nodes["links"]:
        source_id = link["from"]
        target_id = link["to"]
        from_index = link["fromIndex"]
        to_index = link["toIndex"]

        source_node = id_map[source_id]
        target_node = id_map[target_id]
        source_sources = source_node.get_sources()
        target_sinks = target_node.get_sinks()

        connect_sockets(source_sources[from_index], target_sinks[to_index])

    return id_map[nodes["output"]]


def connect_sockets(source, target):
    source.connect_sockets(target)
