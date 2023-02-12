# GNU AGPL v3 License
# Written by John Nunley

import os.path as path
import pytest
import tempfile

from .. import ontario

TEST_IMAGE_PATH = path.join(path.dirname(__file__), "assets", "test.png")


@pytest.fixture
def test_load_from_file():
    """
    Tests the load_from_file method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.process()


@pytest.fixture
def test_save_to_file():
    """
    Tests the save_to_file method.
    """

    with tempfile.TemporaryFile("w+") as file:
        context = ontario.ImageContext()
        builder = ontario.ImageBuilder(context)
        builder.load_from_file(TEST_IMAGE_PATH)
        builder.save_to_file(file)
        builder.process()


@pytest.fixture
def test_composite():
    """
    Tests the composite method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.composite(builder.load_from_file(TEST_IMAGE_PATH))
    builder.process()


@pytest.fixture
def test_invert():
    """
    Tests the invert method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.invert()
    builder.process()


@pytest.fixture
def test_crop():
    """
    Tests the crop method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.crop(0, 0, 100, 100)
    builder.process()


@pytest.fixture
def test_flip():
    """
    Tests the flip method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.flip()
    builder.process()


@pytest.fixture
def test_rotate():
    """
    Tests the rotate method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.rotate(90)
    builder.process()


@pytest.fixture
def test_color_balance():
    """
    Tests the color_balance method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.color_balance(0.5, 0.5, 0.5)
    builder.process()


@pytest.fixture
def test_hue_saturation():
    """
    Tests the hue_saturation method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.hue_saturation(0.5, 0.5)
    builder.process()


@pytest.fixture
def test_unsharp_mask():
    """
    Tests the unsharp_mask method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.unsharp_mask(0.5, 0.5)
    builder.process()


@pytest.fixture
def test_guassian_blur():
    """
    Tests the guassian_blur method.
    """

    context = ontario.ImageContext()
    builder = ontario.ImageBuilder(context)
    builder.load_from_file(TEST_IMAGE_PATH)
    builder.guassian_blur(0.5)
    builder.process()
