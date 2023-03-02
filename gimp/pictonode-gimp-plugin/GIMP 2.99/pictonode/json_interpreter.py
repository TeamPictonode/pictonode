# Created by Parker Nelms

import custom_nodes as cn


def json_interpreter(node_view, json_string: dict, window):

    node_str = 'SrcNode'

    instantiation_dict = {'SrcNode': cn.ImgSrcNode, 'OutNode': cn.OutputNode, 'InvertNode': cn.InvertNode, 'BlurNode': cn.BlurNode}

    for node in json_string["nodes"]:

        node_str = node["template"]
        x_str = node["metadata"]["x"]
        y_str = node["metadata"]["y"] // 2

        if node_str in instantiation_dict:
            # add node at given position
            node_obj = instantiation_dict[node_str](window)
            node_view.add(node_obj)
            node_view.child_set_property(node_obj, "x", x_str)
            node_view.child_set_property(node_obj, "y", y_str)

        else:
            return False

    return True
