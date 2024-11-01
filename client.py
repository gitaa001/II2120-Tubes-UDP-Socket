import socket
import threading
import csv
import os

class ChatClient:
    def __init__(self, server_ip, server_port, username=""):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.users = self.load_users()

    def load_users(self, filename='users.csv'):
        users = {}
        if os.path.exists(filename):
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    username, password = row
                    users[username] = password
        return users

    def save_user(self, username, password, filename='users.csv'):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])

    def send_message(self):
        while True:
            try:
                data = input()
                if data.lower() == "logout":
                    self.logout()
                    break
                message = f"{data}"
                self.client_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            except KeyboardInterrupt:
                self.logout()
                break

    def receive_message(self):
        while True:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                message = data.decode()
                print(message)
            except Exception as e:
                print(f"LOG: Error - {e}")
                break

    def logout(self):
        logout_message = f"LOGOUT:{self.username}"
        self.client_socket.sendto(logout_message.encode(), (self.server_ip, self.server_port))
        print(f"{self.username} berhasil logout. Kembali ke menu utama.\n")

    def authenticate_server(self):
        while True:
            password = input("Masukkan password chatroom: ").strip()
            auth_message = f"AUTH:{password}"
            self.client_socket.sendto(auth_message.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            if response.decode() == "AUTH_SUCCESS":
                print("Berhasil terhubung ke server!")
                return True
            else:
                print("Password salah, coba lagi.")

    def main_menu(self):
        while True:
            print("\n======== MENU =========")
            print("1. Login\n2. Register\n3. Exit")
            action = input(">> Pilih opsi: ").strip()

            if action == '1':
                self.login()
            elif action == '2':
                self.register()
            elif action == '3':
                print("Terima kasih telah menggunakan layanan kami. Sampai jumpa!")
                os._exit(0)
            else:
                print("Pilihan tidak valid. Coba lagi.")

    def login(self):
        print("\n======== LOGIN =========")
        self.username = input("Username: ").strip()
        password = input("Password: ").strip()

        if self.username not in self.users:
            print("Username belum terdaftar. Silakan register.")
            return

        if self.users[self.username] != password:
            print("Password salah. Coba lagi.")
            return

        login_message = f"LOGIN:{self.username}"
        self.client_socket.sendto(login_message.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        if response.decode() == "Login berhasil.":
            print(f"\n======================== {self.username} IS LOGGED IN ============================")
            print("Selamat datang! Silakan ketik 'logout' jika ingin meninggalkan percakapan.")
            print("\n>> Mulai mengirim pesan:")
            self.start_communication()
        else:
            print(response.decode())

    def register(self):
        print("\n======== REGISTER =========")
        new_username = input("Username baru: ").strip()
        new_password = input("Password baru: ").strip()

        if not new_username or not new_password:
            print("Username dan password tidak boleh kosong.")
            return

        if new_username in self.users:
            print("Username sudah terdaftar. Gunakan username lain.")
        else:
            self.save_user(new_username, new_password)
            print("Registrasi berhasil! Silakan login.")
            self.users[new_username] = new_password

    def start_communication(self):
        send_thread = threading.Thread(target=self.send_message)
        receive_thread = threading.Thread(target=self.receive_message)
        send_thread.start()
        receive_thread.start()
        send_thread.join()
        receive_thread.join()


# Run Client
server_ip = input("Masukkan IP Server: ").strip()
server_port = int(input("Masukkan Port Server: ").strip())
client = ChatClient(server_ip, server_port)

if client.authenticate_server():
    client.main_menu()
