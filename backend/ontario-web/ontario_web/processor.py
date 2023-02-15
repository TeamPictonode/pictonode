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
    pipeline = nodes.deserializePipeline(json.loads(pipeline), make_template_table())

    # set metadata for all nodes
    context = ImageContext()
    for node in pipeline.getNodes():
        node.setMetadata(PipelineMetadata(images, context))

    outputNode = pipeline.getOutputNode()
    if outputNode is None:
        raise Exception("No output node.")

    # Get the output
    output = outputNode.getOutputs()[0]
    img = output.getValue()
    if not isinstance(img, ImageBuilder):
        raise Exception(f"Output is not an image; got {type(img)}, {repr(img)}")

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

    def __init__(self, images: ImageManager, context: ImageContext):
        self.images = images
        self.context = context


def make_template_table() -> nodes.TemplateTable[PipelineUnit, PipelineMetadata]:
    table = nodes.TemplateTable()

    # Input node that loads an image from disk
    inputNode = nodes.NodeTemplate(
        lambda args, metadata: [ImageBuilder(
            metadata.context).load_from_file(args[0].getValue())],
        [
            nodes.LinkTemplate(None, -1)
        ],
        [
            nodes.LinkTemplate(None, None)
        ],
        None
    )
    table.addTemplate("input", inputNode)

    # Output node that saves an image to disk
    outputNode = nodes.NodeTemplate(
        lambda args, _: [args[0].getValue()],
        [
            nodes.LinkTemplate(None, "foobar")
        ],
        [
            nodes.LinkTemplate(None, -1)
        ],
        None
    )
    table.addTemplate("output", outputNode)

    def raise_(args, meta):
        raise Exception(f"Not implemented. {args[0].getValue()}")

    def load(arg, meta) -> ImageBuilder:
        val = arg.getValue()
        #print(f"Load: {val}")
        if isinstance(val, ImageBuilder):
            return val
        return ImageBuilder(meta.context).load_from_file(val)

    def composite(args, meta):
        val = load(args[0], meta).composite(load(args[1], meta))
        #nprint(f"Composite: {val}")
        return val

    # Composite node that composes two images
    compositeNode = nodes.NodeTemplate(
        lambda args, meta: [composite(args, meta)],
        [
            nodes.LinkTemplate(None, None),
            nodes.LinkTemplate(None, None)
        ],
        [
            nodes.LinkTemplate(None, "foobar")
        ],
        None
    )
    table.addTemplate("composite", compositeNode)

    return table
