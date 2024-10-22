import socket
import threading

def receive_messages(sock):
    """Fungsi untuk menerima pesan dari server."""
    while True:
        try:
            message, _ = sock.recvfrom(1024)
            print(message.decode())  # Tampilkan pesan yang diterima
        except Exception as e:
            print(f"Terputus dari server: {e}")
            break

# Input dari pengguna
server_ip = input("Masukkan IP Server: ")
server_port = int(input("Masukkan Port Server: "))
username = input("Masukkan Username: ")
password = input("Masukkan Password: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Kirim pesan login ke server
    login_message = f"LOGIN:{username}:{password}"
    client_socket.sendto(login_message.encode(), (server_ip, server_port))
    print("Login request sent...")

    # Terima respon dari server
    response, _ = client_socket.recvfrom(1024)
    response = response.decode()
    print(response)

    if "ERROR" in response:
        print("Login gagal. Program ditutup.")
        client_socket.close()
        exit(1)

    # Mulai thread untuk menerima pesan
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # Kirim pesan ke server
    while True:
        message = input()
        if message.lower() == "exit":
            client_socket.sendto("exit".encode(), (server_ip, server_port))
            print("Keluar dari chat room.")
            break

        # Tampilkan pesan sendiri di layar
        print(f"{username}: {message}")

        # Kirim hanya pesan ke server
        client_socket.sendto(message.encode(), (server_ip, server_port))

except Exception as e:
    print(f"Error: {e}")
finally:
    client_socket.close()
