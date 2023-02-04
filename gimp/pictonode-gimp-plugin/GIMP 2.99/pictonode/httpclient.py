import http.client 
from http.client import HTTPConnection 
import json

# This file was written in its entirety by Parker Nelms and Stephen Foster.

class HTTPClient():
    def __init__(self):
      self.client = HTTPConnection("127.0.0.1",2047)

    def send_image(self, image_data):
      request = self.client.request("POST", "/api/upload_image", body=image_data)
      res = self.client.getresponse()
      print(res.status)
    
    def send_pipeline(self, pipeline: dict):

      """Send a given a SerializedPipeline to the daemon. 
      Returns the resulting image."""

      pipeline = json.dumps(pipeline)

      request = self.client.request("POST", "/api/process_image", body=pipeline)
      res = self.client.getresponse()

      if res.status == 200:
        return request
      
      print("Connection Failed")
      return None

    def close_connection(self):
      self.client.close()
      
http_client = HTTPClient()
    




