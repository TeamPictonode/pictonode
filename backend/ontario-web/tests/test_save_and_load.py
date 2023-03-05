# GNU AGPL v3 License
# Test saving and loading

import tempfile
import zipfile


def getPipeline(image1_id, image2_id):
    return f"""
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


def test_save_and_load(client, image_ids):
    image1_id, image2_id = image_ids

    # Create the pipeline
    pipeline = getPipeline(image1_id, image2_id)

    # Save the pipeline
    response = client.post("/api/save", json=pipeline)
    assert response.status_code == 200

    # Get the zip file as the response body and save it
    zip_file = response.data
    with tempfile.NamedTemporaryFile(suffix=".zip") as temp:
        temp.write(zip_file)
        temp.flush()

        # The zip file should have 3 files, one of them named pipeline.json
        with zipfile.ZipFile(temp.name, "r") as zip_ref:
            assert len(zip_ref.namelist()) == 3
            assert "pipeline.json" in zip_ref.namelist()

        # Load the pipeline
        response = client.post(
            '/api/load',
            content_type='multipart/form-data',
            data=dict(
                file=(open(temp.name, 'rb'), temp.name)
            )
        )
        assert response.status_code == 200

        # The body should be a JSON pipeline
        loadedPipeline = response.json

        # This should be a valid pipeline
        assert loadedPipeline["nodes"]

        # If we process it, it should work
        response = client.post('/api/process', json=loadedPipeline)
        assert response.status_code == 200
