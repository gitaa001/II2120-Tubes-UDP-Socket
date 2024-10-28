import socket
import csv

server_password = "ampunbang"
# Input IP and port
IpAddress = input("Masukkan IP Address: ")
portServer = int(input("Masukkan Port Number: "))

# Create server socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer))  # Bind IP and port

# Initialize clients dictionary
clients = {}

print(f"Chatroom server running on {IpAddress}:{portServer}...")

while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = data.decode()  # Decode message from bytes to string
    username, pesan = message.split("|", 1)

    # Register new client
    if clientAddress not in clients:
        clients[clientAddress] = username
        print(f"New client joined: {username} ({clientAddress})")

    # Broadcast message to all clients
    for client in clients.keys():
        if client != clientAddress:  # Don't send the message back to the sender
            serverSocket.sendto(data, client)

    # Log the received message
    print(f"LOG: Received message from {username} ({clientAddress}): {pesan}")

