# GNU AGPL v3 License
# Written by John Nunley
# libnodepy-based pipeline processor, using ontario as a backend.

import json
import os.path as path
import tempfile

from .image_manager import ImageManager
from . import nodes

from .ontario import ImageContext, ImageBuilder

from typing import Union

PipelineUnit = Union[ImageBuilder, int]


def process(pipeline: str, images: ImageManager, target: str) -> None:
    """
    Processes a pipeline.
    """

    # Deserialize from JSON
    pipeline = nodes.deserializePipeline(json.loads(pipeline))

    # set metadata for all nodes
    for node in pipeline.getNodes():
        node.setMetadata(PipelineMetadata(images))

    outputNode = pipeline.getOutputNode()
    if outputNode is None:
        raise Exception("No output node.")

    # Get the output
    output = outputNode.getOutputs()[0]
    img = output.getValue()
    if not isinstance(img, ImageBuilder):
        raise Exception("Output is not an image.")

    # Save to file
    img.save_to_file(target).process()


class PipelineMetadata:
    """
    Metadata for a pipeline.
    """

    # Image manager
    images: ImageManager

    # Image context
    context: ImageContext

    # Path to save to
    target: str

    def __init__(self, images: ImageManager, context: ImageContext, target: str):
        self.images = images
        self.context = context
        self.target = target


def make_template_table() -> nodes.TemplateTable[PipelineUnit, PipelineMetadata]:
    table = nodes.TemplateTable()

    # Input node that loads an image from disk
    inputNode = nodes.NodeTemplate(
        lambda args, metadata: ImageBuilder(
            metadata.context).load_from_file(args[0]),
        [
            nodes.LinkTemplate(None, -1)
        ],
        [
            nodes.LinkTemplate(None, None)
        ]
    )
    table.addTemplate("input", inputNode)

    # Output node that saves an image to disk
    outputNode = nodes.NodeTemplate(
        lambda args, _: args[0],
        [
            nodes.LinkTemplate(None, None)
        ],
        [
            nodes.LinkTemplate(None, -1)
        ]
    )
    table.addTemplate("output", outputNode)

    # Composite node that composes two images
    compositeNode = nodes.NodeTemplate(
        lambda args, _: args[0].composite(args[1]),
        [
            nodes.LinkTemplate(None, None),
            nodes.LinkTemplate(None, None)
        ],
        [
            nodes.LinkTemplate(None, None)
        ]
    )
    table.addTemplate("composite", compositeNode)

    return table
