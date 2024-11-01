import socket

# Setup password server dan storage untuk client login dan active user
server_password = "ampunbang"
clients = {}  # Key: clientAddress, Value: username
active_users = []  # Array untuk menyimpan active user

# ---------------- Fungsi Kirim Pesan ke Semua Client ---------------------
def broadcast_message(data, exclude_client=None):
    for client in clients.keys():
        if client != exclude_client:  # Cek agar pesan tidak terkirim ke pengirim
            serverSocket.sendto(data.encode(), client)

# Minta IP Address dan Port dari user
IpAddress = input("Masukkan IP Address: ").strip()
portServer = int(input("Masukkan Port Number: ").strip())

# Buat socket server dan bind ke IP dan Port
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((IpAddress, portServer)) 

print(f"Chatroom server running on {IpAddress}:{portServer}...")

# ---------------- Terima dan Tangani Pesan dari Client ------------------
while True:
    data, clientAddress = serverSocket.recvfrom(1024)
    message = data.decode()

    # Proses Autentikasi Server
    if message.startswith("AUTH:"):
        _, password = message.split(":", 1)
        if password == server_password:
            serverSocket.sendto("AUTH_SUCCESS".encode(), clientAddress)
        else:
            serverSocket.sendto("AUTH_FAILED".encode(), clientAddress)
            continue  # Lanjut ke iterasi berikutnya tanpa memberikan akses lebih lanjut

    # Proses Login
    elif message.startswith("LOGIN:"):
        _, username = message.split(":", 1)

        # Cek jika username sudah aktif di active_users
        if username in active_users:
            serverSocket.sendto("ERROR: Username sudah digunakan.".encode(), clientAddress)
        else:
            # Tambahkan pengguna baru ke daftar clients dan active_users
            clients[clientAddress] = username
            active_users.append(username)

            # Notifikasi ke semua pengguna tentang pengguna yang baru bergabung
            login_notification = f"[SERVER]: {username} telah bergabung ke roomchat."
            broadcast_message(login_notification, exclude_client=clientAddress)

            # Kirim respons sukses login ke pengguna
            serverSocket.sendto("Login berhasil.".encode(), clientAddress)
            print(f"New client joined: {username} ({clientAddress})")

    # Proses Logout
    elif message.startswith("LOGOUT:"):
        _, username = message.split(":", 1)

        # Hapus informasi client dari daftar active users dan clients
        if clientAddress in clients and username in active_users:
            print(f"{username} has left the chat. ({clientAddress})")
            del clients[clientAddress]
            active_users.remove(username)

            # Kirim notifikasi ke semua pengguna bahwa client telah keluar
            logout_notification = f"[SERVER]: {username} telah keluar dari chatroom."
            broadcast_message(logout_notification)

    # Teruskan Pesan ke Semua Pengguna jika bukan perintah khusus
    elif message and clientAddress in clients:
        username = clients.get(clientAddress, "Unknown")
        broadcast_message(f"{username}: {message}")

        # Log pesan di server
        print(f"LOG: {username} ({clientAddress}): {message}")
