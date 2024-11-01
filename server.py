import socket
import threading
import os

class ChatServer:
    def __init__(self, ip_address, port, server_password="ampunbang"):
        self.server_password = server_password
        self.ip_address = ip_address
        self.port = port
        self.clients = {}  # Key: clientAddress, Value: username
        self.active_users = []  # Array active user
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.ip_address, self.port))
        print(f"Chatroom server running on {self.ip_address}:{self.port}...")

    def broadcast_message(self, data, exclude_client=None):
        for client in self.clients.keys():
            if client != exclude_client:
                self.server_socket.sendto(data.encode(), client)

    def handle_client_message(self, data, client_address):
        message = data.decode()
        
        if message.startswith("AUTH:"):
            _, password = message.split(":", 1)
            if password == self.server_password:
                self.server_socket.sendto("AUTH_SUCCESS".encode(), client_address)
            else:
                self.server_socket.sendto("AUTH_FAILED".encode(), client_address)

        elif message.startswith("LOGIN:"):
            _, username = message.split(":", 1)
            if username in self.active_users:
                self.server_socket.sendto("ERROR: Username sudah digunakan.".encode(), client_address)
            else:
                self.clients[client_address] = username
                self.active_users.append(username)
                login_notification = f"[SERVER]: {username} telah bergabung ke roomchat."
                self.broadcast_message(login_notification, exclude_client=client_address)
                self.server_socket.sendto("Login berhasil.".encode(), client_address)
                print(f"New client joined: {username} ({client_address})")

        elif message.startswith("LOGOUT:"):
            _, username = message.split(":", 1)
            if client_address in self.clients:
                print(f"{username} has left the chat. ({client_address})")
                del self.clients[client_address]
                self.active_users.remove(username)
                logout_notification = f"[SERVER]: {username} telah keluar dari chatroom."
                self.broadcast_message(logout_notification)

        elif message and client_address in self.clients:
            username = self.clients.get(client_address, "Unknown")
            self.broadcast_message(f"{username}: {message}")
            print(f"LOG: {username} ({client_address}): {message}")

    def start(self):
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            self.handle_client_message(data, client_address)


# Run Server
ip_address = input("Masukkan IP Address: ").strip()
port = int(input("Masukkan Port Number: ").strip())
server = ChatServer(ip_address, port)
server.start()
