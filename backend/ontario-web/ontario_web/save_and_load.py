# GNU AGPL v3 License
# Written by John Nunley

# Save/load functions

import json
import tempfile
import zipfile

from os import path


def save_to_zip(
    image_manager,
    json_pipeline,
    target
):
    """
    Save the JSON pipeline as a zip file
    """

    # Convert to object notation is json_pipeline is a string
    if isinstance(json_pipeline, str):
        json_pipeline = json.loads(json_pipeline)

    with zipfile.ZipFile(target, "w") as zip_file:
        for node in json_pipeline["nodes"]:
            if node["template"] == "input":
                # Get the resulting image path
                values = node["values"]
                id = values["image"]
                image = image_manager.image_path_for_id(id)

                # Save the image
                target_path = f"input_{id}.{image_manager.extension()}"
                zip_file.write(image, target_path)
                node["values"]["image"] = target_path

        # Save the JSON pipeline
        json_pipeline = json.dumps(json_pipeline)
        zip_file.writestr("pipeline.json", json_pipeline)


def load_from_zip(
    image_manager,
    source
):
    """
    Load the JSON pipeline from a zip file
    """

    with zipfile.ZipFile(source, "r") as zip_file:
        # Load the JSON pipeline
        json_pipeline = zip_file.read("pipeline.json")
        json_pipeline = json.loads(json_pipeline)

        for node in json_pipeline["nodes"]:
            if node["template"] == "input":
                # Get the resulting image path
                values = node["values"]
                img_path = values["image"]

                # Load the image
                image = zip_file.read(img_path)
                ext = path.splitext(img_path)[1]
                with tempfile.NamedTemporaryFile(suffix=ext) as temp:
                    temp.write(image)
                    temp.flush()
                    image = temp.name
                    id = image_manager.add_image(image)
                    node["values"]["image"] = id

        return json_pipeline
