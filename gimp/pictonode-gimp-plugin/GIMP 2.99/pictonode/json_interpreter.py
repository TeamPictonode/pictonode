# Created by Parker Nelms

import custom_nodes as cn
import json


def json_interpreter(node_view, window, **kwargs):
    ''' Generate a node graph from a json object format. '''

    filename = kwargs.get("filename")

    json_string = kwargs.get("json_string")
    print(type(json_string))
    print(type(filename))

    if filename:
        if json_string:
            raise Exception("JSONConflict")
        else:
            f = open(filename)
            json_string = json.load(f)
            f.close()

    node_str = 'SrcNode'

    instantiation_dict = {'ImgSrc': cn.ImgSrcNode, 'ImgOut': cn.OutputNode,
                          'Invert': cn.InvertNode, 'GaussBlur': cn.BlurNode,
                          'BrightCont': cn.BrightContNode}

    nodes_loaded = {}

    # Goes through each node and adds a corresponding gtknode object to the given node view
    for node in json_string["nodes"]:

        print("Node start: ", node)

        node_str = node["template"]
        x = node["metadata"]["x"]
        y = node["metadata"]["y"]

        if node_str in instantiation_dict:
            # add node at given position
            node_obj = instantiation_dict[node_str](window)
            node_view.add(node_obj)
            node_obj.set_property("x", x)
            node_obj.set_property("y", y)
            node_obj.set_values(node.get("values"))

            nodes_loaded[node["id"]] = node_obj

        else:
            return False

        print("Node end: ", node)

    # Goes through each link and connects the two nodes it corresponds to
    for link in json_string["links"]:
        from_obj = nodes_loaded.get(link.get("from"))
        to_obj = nodes_loaded.get(link.get("to"))
        from_index = link.get("fromIndex")
        to_index = link.get("toIndex")

        if from_obj and to_obj:
            try:
                from_source = from_obj.get_sources()[from_index]
                to_sink = to_obj.get_sinks()[to_index]
                to_sink.connect_sockets(from_source)
            except Exception:
                raise Exception("JSONCorrupt")
        else:
            raise Exception("JSONCorrupt")

    return True
