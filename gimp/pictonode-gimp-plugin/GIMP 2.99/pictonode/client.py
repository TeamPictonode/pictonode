import os
import socket

# This file was written in its entirety by Parker Nelms and Stephen Foster.


class PluginClient:
    def __init__(self):
        self.HOST_NAME = socket.gethostname()
        self.LOCALHOST_IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = 69

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_controller(self):
        self.client.connect((self.LOCALHOST_IP, self.PORT))
        print("Plugin Socket connected to: ")
        print(
            f"Local Host ({self.HOST_NAME}): {self.LOCALHOST_IP}",
            f"On Port: {self.PORT}")

    def close_connection_to_controller(self):
        self.client.close()

    def send_message_to_controller(self, msg):
        self.client.send(msg.encode('utf-8'))

    def receive_message_from_controller(self):
        print(self.client.recv(1024).decode('utf-8'))

    def send_image_to_controller(self, image):
        file = open(image, "rb")
        image_data = file.read()
        self.client.sendall(image_data)
        file.close()

    def receive_image_from_controller(self, image):
        pass


client = PluginClient()
