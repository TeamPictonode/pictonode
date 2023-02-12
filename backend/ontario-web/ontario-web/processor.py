# GNU AGPL v3 License
# Written by John Nunley
# libnodepy-based pipeline processor, using ontario as a backend.

import json
import os.path as path
import tempfile

from .image_manager import ImageManager
from . import nodes

from ontario import ImageContext, ImageBuilder

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

    def __init__(self, images: ImageManager):
        self.images = images


def make_template_table() -> nodes.TemplateTable[PipelineUnit, PipelineMetadata]:
    table = nodes.TemplateTable()

    # TODO

    return table
