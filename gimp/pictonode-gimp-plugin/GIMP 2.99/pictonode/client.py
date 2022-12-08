import socket
class PluginClient:
    def __init__(self):
        self.HOST_NAME = socket.gethostname()
        self.LOCALHOST_IP = socket.gethostbyname(self.HOST_NAME)
        self.PORT = 69

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_controller(self):
        self.client.connect((self.LOCALHOST_IP, self.PORT))
        print("Plugin Socket connected to: ")
        print(f"Local Host ({self.HOST_NAME}): {self.LOCALHOST_IP}", f"On Port: {self.PORT}")

    def send_message_to_controller(self, msg):
        self.client.send(msg.encode('utf-8'))

    def receive_message_from_controller(self):
        print(self.client.recv(1024).decode('utf-8'))

    def send_image_to_controller(self, image):
        pass

    def receive_image_from_controller(self, image):
        pass

client = PluginClient()

def send_message_to_controller_callback(button, msg):
    client.connect_to_controller()
    client.send_message_to_controller(msg)
    client.receive_message_from_controller()

def send_image_to_controller_callback(button, gegl):
    client.connect_to_controller()
    client.send_image_to_controller(image)
    client.receive_message_from_controller()