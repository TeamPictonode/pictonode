import socket

HOST_NAME = socket.gethostname()
LOCALHOST_IP = socket.gethostbyname(HOST_NAME)
PORT = 69

#Bind Test Controller (server) to Local Host and Port
controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controller.bind((LOCALHOST_IP, PORT))

#Listen for only 1 connection
controller.listen(1)

print("Controller Socket open on: ")
print(f"Local Host ({HOST_NAME}): {LOCALHOST_IP}", f"On Port: {PORT}")

#Accept connection from plugin
plugin_socket, address = controller.accept()
print(f"Connected to {address}")
message = plugin_socket.recv(1024).decode('utf-8')
print(f"Message from client is: {message}")
plugin_socket.send(f"Message Received".encode('utf-8'))
plugin_socket.close()
print(f"Connection {address} ended!")