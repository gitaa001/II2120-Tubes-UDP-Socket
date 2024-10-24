import socket
import threading

SERVER_PASSWORD = "ip4amin"

# Data runtime untuk menyimpan username dan password pengguna
user_data = {}  # Key: username, Value: password
active_users = {}  # Key: username, Value: (addr)

def handle_client_message(sock):
    """Fungsi untuk menangani pesan dari klien."""
    while True:
        try:
            message, addr = sock.recvfrom(1024)
            message = message.decode()

            if message.startswith("AUTH:"):
                # Proses autentikasi password server
                _, server_pass = message.split(":")
                if server_pass == SERVER_PASSWORD:
                    sock.sendto("AUTH_SUCCESS".encode(), addr)
                else:
                    sock.sendto("AUTH_FAILED".encode(), addr)
                    continue

            elif message.startswith("LOGIN:"):
                _, username, password = message.split(":")

                if username in user_data:
                    if user_data[username] == password:  # Verifikasi password
                        if username in active_users:
                            sock.sendto("ERROR: Username sudah aktif.".encode(), addr)
                        else:
                            active_users[username] = addr
                            sock.sendto("Login berhasil.".encode(), addr)
                            print(f"{username} bergabung dari {addr}")
                    else:
                        sock.sendto("ERROR: Password salah.".encode(), addr)

                else:
                    # Registrasi username dan password baru
                    user_data[username] = password
                    active_users[username] = addr
                    sock.sendto("Registrasi dan login berhasil.".encode(), addr)
                    print(f"{username} terdaftar dan login dari {addr}")

            elif message.startswith("LOGOUT:"):
                _, username = message.split(":")
                if username in active_users:
                    del active_users[username]
                    print(f"{username} keluar dari chat.")

            else:
                # Ambil username pengirim dari addr
                sender_username = None
                for username, address in active_users.items():
                    if address == addr:
                        sender_username = username
                        break

                if sender_username:
                    # Broadcast pesan ke semua pengguna dengan format "username: pesan"
                    formatted_message = f"{sender_username}: {message}"
                    print(f"Pesan dari {addr} ({sender_username}): {message}")
                    broadcast_message(sock, formatted_message, addr)

        except Exception as e:
            print(f"Error: {e}")
            break

def broadcast_message(sock, message, sender_addr):
    """Mengirim pesan ke semua pengguna kecuali pengirim."""
    for user, addr in active_users.items():
        if addr != sender_addr:
            sock.sendto(message.encode(), addr)

def start_server():
    server_ip = "0.0.0.0"
    server_port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))
    print(f"Server berjalan di {server_ip}:{server_port}")

    threading.Thread(target=handle_client_message, args=(server_socket,), daemon=True).start()

    while True:
        pass

if __name__ == "__main__":
    start_server()
