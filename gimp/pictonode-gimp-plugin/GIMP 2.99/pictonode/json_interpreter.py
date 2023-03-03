# Created by Parker Nelms

import custom_nodes as cn


def json_interpreter(node_view, json_string: dict, window):

    node_str = 'SrcNode'

    instantiation_dict = {'SrcNode': cn.ImgSrcNode, 'OutNode': cn.OutputNode, 'InvertNode': cn.InvertNode, 'BlurNode': cn.BlurNode}

    nodes_loaded = {}

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
            # node_view.child_set_property(node_obj, "x", x)
            # node_view.child_set_property(node_obj, "y", y)

        else:
            return False
        
    for link in json_string["links"]:
        pass

    return True
