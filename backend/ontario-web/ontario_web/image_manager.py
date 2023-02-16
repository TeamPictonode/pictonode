# GNU AGPL v3 License
# Written by John Nunley

# autopep8 off
from . import ontario
import os
import datetime
from typing import Dict
from gi.repository import Gegl
import gi
gi.require_version('Gegl', '0.4')
# autopep8 on


class ImageManager:
    """
    Manages the images on disk.
    """

    # The root directory for images.
    __root: str

    # Maximum file size we can store on disk.
    __max_file_size: int

    # Current file size.
    __current_file_size: int

    # Map between numerical image IDs and their file paths.
    __image_map: Dict[int, str]

    # The last image ID.
    __last_image_id: int

    # Extension for images.
    __extension: str

    # The amount of time that an image is allowed to live.
    __image_lifetime: datetime.timedelta

    def __init__(self, root: str, max_file_size: int, extension: str):
        os.makedirs(root, exist_ok=True)
        self.__root = root
        self.__max_file_size = max_file_size
        self.__current_file_size = 0
        self.__image_map = {}
        self.__last_image_id = 0
        self.__extension = extension
        self.__image_lifetime = datetime.timedelta(days=1)

    def __clean_up(self) -> None:
        """
        Clears out the oldest images until we are under the maximum file size.
        """

        # Sort the images by creation time.
        sorted_images = sorted(self.__image_map.items(),
                               key=lambda x: x[1].creation_time)

        # Remove images that are more than a day old.
        for image_id, image_info in sorted_images:
            remove_image = False
            if datetime.datetime.now() - image_info.creation_time > self.__image_lifetime:
                remove_image = True

            # If we're over quote, remove the image.
            if self.__current_file_size > self.__max_file_size:
                remove_image = True

            if remove_image:
                self.__current_file_size -= image_info.size
                image_info.delete()
                del self.__image_map[image_id]

    def add_image(self, path: str) -> int:
        """
        Adds an image to the image manager.
        """

        # Create a new image ID.
        image_id = self.__last_image_id
        self.__last_image_id += 1

        # Create the image path.
        image_path = os.path.join(
            self.__root, f"{image_id}.{self.__extension}")

        if not os.path.exists(path):
            raise Exception(f"Source image {path} does not exist.")
        if os.stat(path).st_size == 0:
            raise Exception(f"Source image {path} is empty.")

        # Transcode the image from its current format to the desired format.
        context = ontario.ImageContext()
        ontario.ImageBuilder(context).load_from_file(
            path).save_to_file(image_path).process()

        if not os.path.exists(image_path):
            raise Exception(f"Image {image_path} does not exist.")
        
        # get the image size
        image_size = os.path.getsize(image_path)

        # Add the image to the image map.
        image_info = _ImageInfo(image_id, image_path, image_size)
        self.__image_map[image_id] = image_info

        # Update the current file size.
        self.__current_file_size += image_size

        # If we're over quota, clean up.
        if self.__current_file_size > self.__max_file_size:
            self.__clean_up()

        return image_id

    def image_path_for_id(self, image_id: int) -> str:
        """
        Returns the image path for the given image ID.
        """

        return self.__image_map[image_id].path

    def clean_up(self) -> None:
        """
        Cleans up the image manager.
        """

        self.__clean_up()


class _ImageInfo:
    """
    A class for storing image information.
    """

    # The image ID.
    id: int

    # The image path.
    path: str

    # The image size.
    size: int

    # The image creation time.
    creation_time: datetime.datetime

    def __init__(self, id: int, path: str, size: int):
        self.id = id
        self.path = path
        self.size = size
        self.creation_time = datetime.datetime.now()

    def delete(self) -> None:
        """
        Deletes the image.
        """

        os.remove(self.path)
