# GNU AGPL v3 License

import json
import pytest
import os.path as path
import tempfile

import flask
import os
import shutil

def _open_file(path):
    with open(path, 'rb') as file:
        return file.read()

def test_process(client):
    # Upload it to the client twice
    # Note: /api/upload_image takes a form with a file named "image"
    def upload_image(p):
      data = dict(
        image = (open(p, 'rb'), p)
      )
      response = client.post(
        '/api/upload_image',
        content_type='multipart/form-data',
        data=data
      )
      assert response.status_code == 200
      return response.json['id']

    p1 = path.join(path.dirname(__file__), "assets", "test1.png")
    p2 = path.join(path.dirname(__file__), "assets", "test2.png")

    # Copy the file to a temporary location
    # This is necessary because the file is opened in the upload_image function
    # and cannot be opened again
    with tempfile.TemporaryDirectory() as temp:
        newpath = path.join(temp, "test-image.png")
        shutil.copy(p1, newpath)
        image1_id = upload_image(newpath)
        shutil.copy(p2, newpath)
        image2_id = upload_image(newpath)

    # Create a pipeline
    pipeline = f"""
    {{
      "nodes": [
        {{
          "id": 0,
          "template": "input",
          "values": {{
            "image": {image1_id}
          }}
        }},
        {{
          "id": 1,
          "template": "input",
          "values": {{
            "image": {image2_id}
          }}
        }},
        {{
          "id": 2,
          "template": "composite"
        }},
        {{
          "id": 3,
          "template": "output"
        }}
      ],
      "links": [
        {{
          "id": 4,
          "from": 0,
          "to": 2,
          "fromIndex": 0,
          "toIndex": 0
        }},
        {{
          "id": 5,
          "from": 1,
          "to": 2,
          "fromIndex": 0,
          "toIndex": 1
        }},
        {{
          "id": 6,
          "from": 2,
          "to": 3,
          "fromIndex": 0,
          "toIndex": 0
        }}
      ],
      "output": 3
    }}
    """

    # Process the pipeline
    response = client.post('/api/process', json=pipeline)
    assert response.status_code == 200


