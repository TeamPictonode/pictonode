import unittest
import sys
import os

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# autopep8 off
import gi  # noqa
gi.require_version("GIRepository", "2.0")
from gi.repository import GIRepository  # noqa

GIRepository.Repository.prepend_search_path(
    os.path.realpath(
        os.path.dirname(
            os.path.abspath(__file__)) +
        "/output/introspection"))

GIRepository.Repository.prepend_library_path(
    os.path.realpath(
        os.path.dirname(
            os.path.abspath(__file__)) +
        "/output/libs"))

gi.require_version("GtkNodes", "0.1")
from gi.repository import GtkNodes  # noqa
# autopep8 on


class TestJSONGenerator(unittest.TestCase):

    def test_json_generator_output(self):
        # import needed modules
        from pictonode import json_generator, custom_nodes

        # create empty NodeView
        node_view = GtkNodes.NodeView()

        # add nodes to NodeView
        node_view.add(custom_nodes.OutputNode(node_window=None))
        node_view.add(custom_nodes.CompositeNode(node_window=None))
        node_view.add(custom_nodes.InvertNode(node_window=None))
        node_view.add(custom_nodes.BlurNode(node_window=None))

        # set basis for correct json representation
        json_true = {'nodes':
                     [{'id': 0,
                       'template': 'OutNode',
                       'values': {},
                       'metadata': {'x': 0,
                                    'y': 0}},
                      {'id': 1,
                       'template': 'CompNode',
                       'values': {'opacity': 1,
                                  'x': 1000,
                                  'y': 100,
                                  'scale': 1},
                       'metadata': {'x': 0,
                                    'y': 0}},
                      {'id': 2,
                       'template': 'InvertNode',
                       'values': {},
                       'metadata': {'x': 0,
                                    'y': 0}},
                      {'id': 3,
                       'template': 'BlurNode',
                       'values': {'std_dev_x': 1.5,
                                  'std_dev_y': 1.5},
                       'metadata': {'x': 0,
                                    'y': 0}}],
                     'links': [],
                     'output': 0}

        # generate json represention given NodeView
        json_result = json_generator.serialize_nodes(node_view=node_view)

        # compare results using the python unittest library/objects
        self.assertEqual(json_result, json_true)

if __name__ == '__main__':
    unittest.main()
