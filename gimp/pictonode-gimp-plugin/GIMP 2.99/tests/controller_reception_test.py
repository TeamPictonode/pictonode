import os
import socket

HOST_NAME = socket.gethostname()
LOCALHOST_IP = socket.gethostbyname(HOST_NAME)
PORT = 2407

#Bind Test Controller (server) to Local Host and Port
controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controller.bind((LOCALHOST_IP, PORT))

#Listen for only 1 connection
controller.listen(1)

print("Controller Socket open on: ")
print(f"Local Host ({HOST_NAME}): {LOCALHOST_IP}", f"On Port: {PORT}")

#Accept connection from plugin
plugin_socket, address = controller.accept()
plugin_socket.settimeout(1.0)
print(f"Connected to {address}")

#Message for right now is file size being sent
message = plugin_socket.recv(1024).decode('utf-8')
print(f"Message from client is: {message}")
plugin_socket.send(f"Controller->Plugin: Message Received. Please start image transmission".encode('utf-8'))

OUTPUT_DIR = f"{os.path.dirname(os.path.abspath(__file__))}"
OUTPUT = f"{OUTPUT_DIR}\\output.png"
output_file = open(OUTPUT, "wb")

image_data = plugin_socket.recv(1024)
output_file.write(image_data)

try:
    while len(image_data) != 0:
        image_data = plugin_socket.recv(1024)
        output_file.write(image_data)
except Exception as inst:
    if inst == TimeoutError:
        pass

output_file.close()
plugin_socket.send(f"Controller->Plugin: Transmission Received".encode('utf-8'))

plugin_socket.close()
print(f"Connection {address} ended!")