# Created by Parker Nelms

import json

def serialize_nodes(node_view):

    ''' Serializes a GtkNode.NodeView into a JSON string'''

    json_string = {}
    output_sockets: dict = {}

    node_list = []
    link_list = []

    # serialize the nodes
    for node in node_view.get_children():
        node_dict = {}
        node_dict["id"] = node.get_property("id")
        node_dict["template"] = str(node.__gtype_name__)
        node_dict["values"] = node.get_values()
        node_dict["metadata"] = {"x": node.get_property("x"),
                                 "y": node.get_property("y")}

        node_list.append(node_dict)

        socket_index = 0
        for source in node.get_sources():
            output_sockets[source] = [node.get_property("id"), socket_index]
            socket_index += 1

    # serialize the links, requires a second pass through the nodes
    link_id = 0
    for node in node_view.get_children():
        sink_index = 0
        for sink in node.get_sinks():
            if not sink.get_input():
                continue

            link_dict = {}
            link_dict["id"] = link_id
            link_dict["from"] = output_sockets[sink.get_input()][0]
            link_dict["to"] = node.get_property("id")
            link_dict["fromIndex"] = output_sockets[sink.get_input()][1]
            link_dict["toIndex"] = sink_index
            link_dict["metadata"] = {}

            link_list.append(link_dict)
            link_id += 1
            sink_index += 1

    json_string["nodes"] = node_list
    json_string["links"] = link_list

    return json_string
