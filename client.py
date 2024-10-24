import socket
import threading

def receive_messages(sock):
    """Menerima pesan dari server."""
    while True:
        try:
            message, _ = sock.recvfrom(1024)
            print(message.decode())
        except Exception as e:
            print(f"Terputus dari server: {e}")
            break

def start_client():
    while True:
        # Input dari pengguna
        server_ip = input("Masukkan IP Server: ")
        server_port = int(input("Masukkan Port Server: "))
        server_password = input("Masukkan Password Server: ")

        username = input("Masukkan Username: ")
        password = input("Masukkan Password: ")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # Kirim password server terlebih dahulu
            auth_message = f"AUTH:{server_password}"
            client_socket.sendto(auth_message.encode(), (server_ip, server_port))
            auth_response, _ = client_socket.recvfrom(1024)
            auth_response = auth_response.decode()

            if auth_response == "AUTH_FAILED":
                print("Password server salah!")
                client_socket.close()
                continue

            # Kirim pesan login setelah autentikasi server berhasil
            login_message = f"LOGIN:{username}:{password}"
            client_socket.sendto(login_message.encode(), (server_ip, server_port))
            print("Login request sent...")

            # Terima respon dari server
            response, _ = client_socket.recvfrom(1024)
            response = response.decode()
            print(response)

            if "ERROR" in response:
                ulangi = input("Login gagal. Anda ingin mencoba lagi? (Y/N): ").strip().lower()
                if ulangi == 'y':
                    client_socket.close()
                    continue  # Ulangi input dari awal
                else:
                    print("Program berhenti. Terima kasih telah menggunakan layanan kami!")
                    exit()

            # Mulai thread untuk menerima pesan
            threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

            # Kirim pesan ke server
            while True:
                message = input()
                if message.lower() == "exit":
                    client_socket.sendto(f"LOGOUT:{username}".encode(), (server_ip, server_port))
                    print("Keluar dari chat room.")
                    break

                print(f"{username}: {message}")
                client_socket.sendto(message.encode(), (server_ip, server_port))

        except Exception as e:
            print(f"Error: {e}")

        finally:
            client_socket.close()

if __name__ == "__main__":
    start_client()
