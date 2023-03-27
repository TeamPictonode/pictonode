# GNU AGPL v3 License
# Written by John Nunley
# libnodepy-based pipeline processor, using ontario as a backend.

import json

from .image_manager import ImageManager
from . import nodes

from .ontario import ImageContext, ImageBuilder

from typing import Union

PipelineUnit = Union[ImageBuilder, int]


def process(pipeline, images: ImageManager, target: str) -> None:
    """
    Processes a pipeline.
    """

    if isinstance(pipeline, str):
        pipeline = json.loads(pipeline)

    # Deserialize from JSON
    pipeline = nodes.deserializePipeline(pipeline, make_template_table())

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
    if isinstance(img, int):
        img = ImageBuilder(context).load_from_file(
            images.image_path_for_id(img))
    if not isinstance(img, ImageBuilder):
        raise Exception(
            f"Output is not an image; got {type(img)}, {repr(img)}")

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


def make_template_table(
) -> nodes.TemplateTable[PipelineUnit, PipelineMetadata]:
    table = nodes.TemplateTable()

    # Input node that loads an image from disk
    inputNode = nodes.NodeTemplate(
        lambda args, metadata: [args[0].getValue()],
        [
            nodes.LinkTemplate(None, -1, "image")
        ],
        [
            nodes.LinkTemplate(None, None, "image")
        ],
        None
    )
    inputNode.insertNamedOutput("image", 0)
    table.addTemplate("ImgSrc", inputNode)

    # Output node that saves an image to disk
    outputNode = nodes.NodeTemplate(
        lambda args, _: [args[0].getValue()],
        [
            nodes.LinkTemplate(None, "foobar", None)
        ],
        [
            nodes.LinkTemplate(None, -1, None)
        ],
        None
    )
    table.addTemplate("ImgOut", outputNode)

    def raise_(args, meta):
        raise Exception(f"Not implemented. {args[0].getValue()}")

    def load(arg, meta) -> ImageBuilder:
        val = arg.getValue()
        if isinstance(val, ImageBuilder):
            return val
        img_path = meta.images.image_path_for_id(val)
        return ImageBuilder(meta.context).load_from_file(img_path)

    def composite(args, meta):
        val = load(args[0], meta).composite(
            load(args[1], meta),
        )
        return val

    # Composite node that composes two images
    compositeNode = nodes.NodeTemplate(
        lambda args, meta: [composite(args, meta)],
        [
            nodes.LinkTemplate(None, None, None),
            nodes.LinkTemplate(None, None, None)
        ],
        [
            nodes.LinkTemplate(None, "foobar", None)
        ],
        None
    )
    table.addTemplate("CompOver", compositeNode)

    # Invert node that inverts an image
    invertNode = nodes.NodeTemplate(
        lambda args, meta: [load(args[0], meta).invert()],
        [
            nodes.LinkTemplate(None, None, None)
        ],
        [
            nodes.LinkTemplate(None, "foobar", None)

        ],
        None
    )
    table.addTemplate("Invert", invertNode)

    # Adjust brightness/contrast
    brightContNode = nodes.NodeTemplate(
        lambda args, meta: [
            load(args[0], meta).brightness_contrast(args[1], args[2])],
        [
            nodes.LinkTemplate(None, None, None),
            nodes.LinkTemplate(None, None, "brightness"),
            nodes.LinkTemplate(None, None, "contrast")
        ],
        [
            nodes.LinkTemplate(None, "foobar2", None)
        ],
        None
    )
    table.addTemplate("BrightCont", brightContNode)

    guassBlur = nodes.NodeTemplate(
        lambda args, meta: [
            load(args[0], meta).gaussian_blur(args[1], args[2])],
        [
            nodes.LinkTemplate(None, None, None),
            nodes.LinkTemplate(None, None, "std_dev_x"),
            nodes.LinkTemplate(None, None, "std_dev_y")
        ],
        [
            nodes.LinkTemplate(None, "foobar2", None)
        ],
        None
    )
    table.addTemplate("GaussBlur", guassBlur)

    return table
