import os
import socket

# This file was written in its entirety by Parker Nelms and Stephen Foster.

class PluginClient:
    def __init__(self):
        self.HOST_NAME = socket.gethostname()
        self.LOCALHOST_IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = 2407

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_controller(self):
        self.client.connect((self.LOCALHOST_IP, self.PORT))
        print("Plugin Socket connected to: ")
        print(f"Local Host ({self.HOST_NAME}): {self.LOCALHOST_IP}", f"On Port: {self.PORT}")

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

    def receive_user_update(self):
        """Takes in user information updates from daemon.
        Format required is json."""

        self.client.listen(1)

        print("Controller Socket open on: ")
        print(f"Local Host ({HOST_NAME}): {LOCALHOST_IP}", f"On Port: {PORT}")

        #Accept connection from daemon
        plugin_socket, address = self.client.accept()
        plugin_socket.settimeout(1.0)
        print(f"Connected to {address}")

        #Message for right now is file size being sent
        message = plugin_socket.recv(1024).decode('utf-8')
        print(f"Message from daemon is: {message}")
        plugin_socket.send(f"Controller->Plugin: Message Received. Please start data transmission".encode('utf-8'))

        return self.client.recv(1024).decode('utf-8')

    def receive_image_from_controller(self, image):
        pass

client = PluginClient()