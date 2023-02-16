#  GNU AGPL v3 License
# Written by John Nunley

import os.path as path
import pytest
import tempfile

import ontario
#from ..ontario import ImageBuilder, ImageContext

TEST_IMAGE_PATH = path.join(path.dirname(__file__), "assets", "test-image.png")
TEST_IMAGE1_PATH = path.join(path.dirname(__file__), "assets", "test1.png")
TEST_IMAGE2_PATH = path.join(path.dirname(__file__), "assets", "test2.png")


def test_load_from_file():
    """
    Tests the load_from_file method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.process()


def test_save_to_file():
    """
    Tests the save_to_file method.
    """

    with tempfile.TemporaryFile("w+") as file:
        context = ontario.ImageContext()
        builder = ontario.ImageBuilder(context)
        builder.load_from_file(TEST_IMAGE_PATH)
        builder.save_to_file(file.name)
        builder.process()


def test_composite():
    """
    Tests the composite method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE1_PATH)
    builder.composite(builder.load_from_file(TEST_IMAGE2_PATH), 0, 0, 0, 1)
    builder.process()


def test_invert():
    """
    Tests the invert method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.invert()
    builder.process()


def test_crop():
    """
    Tests the crop method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.crop(0, 0, 100, 100)
    builder.process()


def test_rotate():
    """
    Tests the rotate method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.rotate(50, 50, 90)
    builder.process()


def test_color_balance():
    """
    Tests the color_balance method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.color_balance(0.5, 0.5, 0.5)
    builder.process()


def test_hue_saturation():
    """
    Tests the hue_saturation method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.hue_chroma_lightness(30, 30, 30)
    builder.process()


def test_unsharp_mask():
    """
    Tests the unsharp_mask method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.unsharp_mask(0.5, 0.5)
    builder.process()

