import socket

server_password = "ampunbang"
clients = {}  # Key: clientAddress, Value: username
active_users = []  # Array active user

# ---------------- KIRIM PESAN KE CLIENT ---------------------
def broadcast_message(data, exclude_client=None):
    for client in clients.keys():
        if client != exclude_client:  # Cek jika bukan pengirim
            serverSocket.sendto(data.encode(), client)


IpAddress = input("Masukkan IP Address: ").strip()
portServer = int(input("Masukkan Port Number: ").strip())

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer)) 

print(f"Chatroom server running on {IpAddress}:{portServer}...")

# -------------- TERIMA PESAN DARI CLIENT ------------------
while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = data.decode()

    # Proses login dengan autentikasi password server
    if message.startswith("AUTH:"):
        _, password = message.split(":", 1)
        if password == server_password:
            serverSocket.sendto("AUTH_SUCCESS".encode(), clientAddress)
        else:
            serverSocket.sendto("AUTH_FAILED".encode(), clientAddress)
            continue

    elif message.startswith("LOGIN:"):
        _, username = message.split(":", 1)

        if username in active_users:
            serverSocket.sendto("ERROR: Username sudah digunakan.".encode(), clientAddress)
        else:
            clients[clientAddress] = username
            active_users.append(username)

            # Notifikasi login
            login_notification = f"[SERVER]: {username} telah bergabung ke roomchat."
            broadcast_message(login_notification, exclude_client=clientAddress)

            serverSocket.sendto("Login berhasil.".encode(), clientAddress)
            print(f"New client joined: {username} ({clientAddress})")

    elif message.startswith("LOGOUT:"): # CLIENT LOGOUT
        _, username = message.split(":", 1)

        if clientAddress in clients:
            print(f"{username} has left the chat. ({clientAddress})")
            del clients[clientAddress]
            active_users.remove(username)

            logout_notification = f"[SERVER]: {username} telah keluar dari chatroom."
            broadcast_message(logout_notification)  

    elif message and clientAddress in clients: # Teruskan pesan
        username = clients.get(clientAddress, "Unknown")
        broadcast_message(f"{username}: {message}")

        # Log pesan di server
        print(f"LOG: {username} ({clientAddress}): {message}")
