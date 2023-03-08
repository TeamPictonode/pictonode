# Created by Parker Nelms


def serialize_nodes(node_view):

    ''' Serializes a GtkNode.NodeView into a JSON string'''

    json_string = {}
    output_sockets: dict = {}

    node_list = []
    link_list = []

    node_indices = []

    # serialize the nodes
    for node in node_view.get_children():
        node_dict = {}
        node_id = node.get_property("id")
        node_dict["id"] = node_id
        node_indices.append(node_id)
        node_dict["template"] = str(node.__gtype_name__)
        node_dict["values"] = node.get_values()
        node_dict["metadata"] = {"x": node.get_property("x"),
                                 "y": node.get_property("y"),
                                 "expanded": node.get_expanded()}

        node_list.append(node_dict)

        socket_index = 0
        for source in node.get_sources():
            output_sockets[source] = [node.get_property("id"), socket_index]
            socket_index += 1

    # serialize the links, requires a second pass through the nodes
    link_id = 0
    for node in node_view.get_children():
        for sink_index, sink in enumerate(node.get_sinks()):
            if not sink.get_input():
                continue

            # ensure no clash between node ids and link ids
            while link_id in node_indices:
                link_id += 1

            link_dict = {}
            link_dict["id"] = link_id
            link_dict["from"] = output_sockets[sink.get_input()][0]
            link_dict["to"] = node.get_property("id")
            link_dict["fromIndex"] = output_sockets[sink.get_input()][1]
            link_dict["toIndex"] = sink_index
            link_dict["metadata"] = {}

            link_list.append(link_dict)
            link_id += 1

    json_string["nodes"] = node_list
    json_string["links"] = link_list

    # set output node id if it exist and sets it to null if not
    try:
        json_string["output"] = list(filter(lambda srcnode: srcnode["template"] == "ImgOut", json_string["nodes"]))[0]["id"]
    except IndexError:
        json_string["output"] = None

    return json_string
