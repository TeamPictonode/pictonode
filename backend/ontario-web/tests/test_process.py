# GNU AGPL v3 License

import json
import pytest
import os.path as path

import flask

def _open_file(path):
    with open(path, 'rb') as file:
        return file.read()

def test_process(client):
    # Open two image files to composite.
    image1 = _open_file(path.join(path.dirname(__file__), "assets", "test.png"))

    # Upload it to the client twice
    # Note: /api/upload_image takes a form with a file named "image"
    def upload_image(image):
      response = client.post('/api/upload_image', data={'image': (image, 'test.png')})
      assert response.status_code == 200
      return response.json['id']

    image1_id = upload_image(image1)
    image2_id = upload_image(image1)

    # Create a pipeline
    pipeline = f"""
    {{
      nodes: [
        {{
          id: 0,
          template: "input",
        }},
        {{
          id: 1,
          template: "input",
        }},
        {{
          id: 2,
          template: "composite",
        }},
        {{
          id: 3,
          template: "output",
        }},
      ],
      edges: [
        {{
          id: 4,
          from: 0,
          to: 2,
          fromIndex: 0,
          toIndex: 0,
          defaultValue: {image1_id}
        }},
        {{
          id: 5,
          from: 1,
          to: 2,
          fromIndex: 0,
          toIndex: 1,
          defaultValue: {image2_id}
        }},
        {{
          id: 6,
          from: 2,
          to: 3,
          fromIndex: 0,
          toIndex: 0,
        }},
      ],
      output: 3
    }}
    """

    # Process the pipeline
    response = client.post('/api/process', json=json.loads(pipeline))
    assert response.status_code == 200
