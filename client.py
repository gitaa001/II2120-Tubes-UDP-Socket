import socket
import threading
import csv
import os

class ChatClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None  # Inisialisasi awal client_socket sebagai None
        self.username = ""
        self.is_logged_in = False
        self.users = self.load_users()
        self.stop_event = threading.Event()  # Event untuk menghentikan thread

    def load_users(self, filename='users.csv'):
        """Load user data from CSV file."""
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
        """Save new user data to CSV file."""
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])

    def send_message(self):
        """Handle sending messages to the server."""
        while self.is_logged_in:
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
        """Handle receiving messages from the server."""
        while self.is_logged_in:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                message = data.decode()
                print(message)
            except Exception as e:
                if self.stop_event.is_set():
                    break  # Hentikan thread jika stop_event disetel
                print(f"LOG: Error - {e}")

    def logout(self):
        """Logout the current user and return to the main menu."""
        logout_message = f"LOGOUT:{self.username}"
        self.client_socket.sendto(logout_message.encode(), (self.server_ip, self.server_port))
        print(f"{self.username} berhasil logout. Kembali ke menu utama.\n")
        self.is_logged_in = False
        self.stop_event.set()  # Set stop_event untuk menghentikan thread
        self.client_socket.close()  # Tutup koneksi soket

    def authenticate_server(self):
        """Authenticate with the server before accessing chat functions."""
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
        """Display the main menu and handle user options."""
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
        """Handle user login and connect to the server."""
        print("\n======== LOGIN =========")
        self.username = input("Username: ").strip()
        password = input("Password: ").strip()

        if self.username not in self.users:
            print("Username belum terdaftar. Silakan register.")
            return

        if self.users[self.username] != password:
            print("Password salah. Coba lagi.")
            return

        # Buat soket baru untuk setiap kali login
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        login_message = f"LOGIN:{self.username}"
        self.client_socket.sendto(login_message.encode(), (self.server_ip, self.server_port))
        
        response, _ = self.client_socket.recvfrom(1024)
        if response.decode() == "Login berhasil.":
            print(f"\n======================== {self.username} IS LOGGED IN ============================")
            print("Selamat datang! Silakan ketik 'logout' jika ingin meninggalkan percakapan.")
            print("\n>> Mulai mengirim pesan:")
            self.is_logged_in = True
            self.start_communication()
        else:
            print(response.decode())

    def register(self):
        """Handle new user registration."""
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
        """Start threads for sending and receiving messages."""
        send_thread = threading.Thread(target=self.send_message)
        receive_thread = threading.Thread(target=self.receive_message)
        send_thread.start()
        receive_thread.start()
        send_thread.join()
        receive_thread.join()

        # Setelah logout, kembali ke menu utama
        self.main_menu()


# Run Client
server_ip = input("Masukkan IP Server: ").strip()
server_port = int(input("Masukkan Port Server: ").strip())
client = ChatClient(server_ip, server_port)

# Autentikasi sebelum mengakses menu utama
client.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Buat soket awal untuk autentikasi server
if client.authenticate_server():
    client.main_menu()
