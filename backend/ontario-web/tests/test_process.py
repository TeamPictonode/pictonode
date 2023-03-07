# GNU AGPL v3 License

def test_process(client, image_ids):
    image1_id, image2_id = image_ids

    # Create a pipeline
    pipeline = f"""
    {{
      "nodes": [
        {{
          "id": 0,
          "template": "ImgSrc",
          "values": {{
            "image": {image1_id}
          }}
        }},
        {{
          "id": 1,
          "template": "ImgSrc",
          "values": {{
            "image": {image2_id}
          }}
        }},
        {{
          "id": 2,
          "template": "CompOver"
        }},
        {{
          "id": 3,
          "template": "ImgOut"
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
