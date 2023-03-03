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

    instantiation_dict = {'SrcNode': cn.ImgSrcNode, 'OutNode': cn.OutputNode, 'InvertNode': cn.InvertNode, 'BlurNode': cn.BlurNode}

    nodes_loaded = {}

    # Goes through each node and adds a corresponding gtknode object to the given node view
    for node in json_string["nodes"]:

        node_str = node["template"]
        x = node["metadata"]["x"]
        y = node["metadata"]["y"]

        print("x: ", x)
        print("y: ", y)

        if node_str in instantiation_dict:
            # add node at given position
            node_obj = instantiation_dict[node_str](window)
            node_view.add(node_obj)
            node_obj.set_property("x", x)
            node_obj.set_property("y", y)

            nodes_loaded[node["id"]] = node_obj

        else:
            return False

    # Goes through each link and connects the two nodes it corresponds to
    for link in json_string["links"]:
        pass

    return True
