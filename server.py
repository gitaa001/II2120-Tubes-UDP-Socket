import socket

# Konfigurasi Server
SERVER_IP = "0.0.0.0"  # Menerima koneksi dari semua IP
SERVER_PORT = 12345
PASSWORD = "ip4amin"  # Password untuk bergabung ke chatroom
BUFFER_SIZE = 1024

# Membuat socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

print(f"Server berjalan di {SERVER_IP}:{SERVER_PORT}")

clients = {}  # {client_address: username}
usernames = set()  # Menyimpan username untuk memastikan keunikan

try:
    while True:
        # Menerima pesan dari client
        message, client_address = server_socket.recvfrom(BUFFER_SIZE)
        decoded_msg = message.decode()

        # Jika client belum terdaftar, proses login
        if client_address not in clients:
            if decoded_msg.startswith("LOGIN:"):
                username, password = decoded_msg.split(":")[1:]

                # Verifikasi password dan keunikan username
                if password == PASSWORD:
                    if username not in usernames:
                        # Simpan alamat dan username client
                        clients[client_address] = username
                        usernames.add(username)
                        print(f"{username} bergabung dari {client_address}")

                        server_socket.sendto("Berhasil login!".encode(), client_address)
                    else:
                        server_socket.sendto("ERROR: Username sudah dipakai.".encode(), client_address)
                else:
                    server_socket.sendto("ERROR: Password salah.".encode(), client_address)
            continue  # Kembali ke awal loop jika proses login

        # Jika client terdaftar, terima dan teruskan pesan
        username = clients[client_address]

        if decoded_msg.lower() == "exit":  # Client keluar
            print(f"{username} keluar dari chat room.")
            del clients[client_address]
            usernames.remove(username)  # Hapus dari daftar username
            server_socket.sendto("Anda keluar dari chat room.".encode(), client_address)
            continue  # Kembali ke awal loop

        # Tampilkan pesan di server
        print(f"{username} ({client_address}): {decoded_msg}")

        # Teruskan pesan ke semua client lain
        for client in clients:
            if client != client_address:
                server_socket.sendto(f"{username}: {decoded_msg}".encode(), client)

except KeyboardInterrupt:
    print("\nServer dihentikan.")
finally:
    server_socket.close()
