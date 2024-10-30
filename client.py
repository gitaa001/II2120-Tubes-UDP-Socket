import socket
import threading
import csv
import os

# ----------------- READ DATA USER -----------------
def load_users(filename='users.csv'):
    users = {}
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                username, password = row
                users[username] = password
    return users

# ----------------- SAVE DATA USER -----------------
def save_user(username, password, filename='users.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

# --------------- FUNGSI KIRIM PESAN -----------------
def send_message():
    while True:
        try:
            data = input()  # Input pesan dari user
            if data.lower() == "logout":
                logout()
                break

            message = f"{data}" 
            client_socket.sendto(message.encode(), (server_ip, server_port))
        except KeyboardInterrupt:
            logout()
            break

# ------------- FUNGSI TERIMA PESAN ----------------
def receive_message():
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            message = data.decode()
            print(message)  
        except Exception as e:
            print(f"LOG: Error - {e}")
            break

# ----------------- FUNGSI LOGOUT ------------------
def logout():
    logout_message = f"LOGOUT:{username}"
    client_socket.sendto(logout_message.encode(), (server_ip, server_port))
    print(f"{username} berhasil logout. Kembali ke menu utama.\n")

# ------------- FUNGSI AUTENTIKASI SERVER ----------
def authenticate_server():
    while True:
        password = input("Masukkan password chatroom: ").strip()
        auth_message = f"AUTH:{password}"
        client_socket.sendto(auth_message.encode(), (server_ip, server_port))

        response, _ = client_socket.recvfrom(1024)
        if response.decode() == "AUTH_SUCCESS":
            print("Berhasil terhubung ke server!")
            return True  
        else:
            print("Password salah, coba lagi.")

# --------------- FUNGSI MENU UTAMA ----------------
def main_menu():
    global username  # Untuk digunakan di seluruh fungsi

    while True:
        print("\n======== MENU =========")
        print("1. Login\n2. Register\n3. Exit")
        action = input(">> Pilih opsi: ").strip()

        if action == '1':
            print("\n======== LOGIN =========")
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            if username not in users:
                print("Username belum terdaftar. Silakan register.")
                continue

            if users[username] != password:
                print("Password salah. Coba lagi.")
                continue

            # Kirim pesan login ke server
            login_message = f"LOGIN:{username}"
            client_socket.sendto(login_message.encode(), (server_ip, server_port))

            response, _ = client_socket.recvfrom(1024)
            if response.decode() == "Login berhasil.":
                print(f"\n======================== {username} IS LOGGED IN ============================")
                print(f"Selamat datang! Silakan ketik 'logout' jika ingin meninggalkan percakapan.")
                print("\n>> Mulai mengirim pesan:")
                break  
            else:
                print(response.decode())

        elif action == '2':
                print("\n======== REGISTER =========")
                new_username = input("Username baru: ").strip()
                new_password = input("Password baru: ").strip()

                if not new_username or not new_password:
                    print("Username dan password tidak boleh kosong.")
                    continue

                if new_username in users:
                    print("Username sudah terdaftar. Gunakan username lain.")
                else:
                    save_user(new_username, new_password)
                    print("Registrasi berhasil! Silakan login.")
                    users[new_username] = new_password
                    break

        elif action == '3':
            print("Terima kasih telah menggunakan layanan kami. Sampai jumpa!")
            os._exit(0)

        else:
            print("Pilihan tidak valid. Coba lagi.")

# -------------- INISIASI KONEKSI ------------------
server_ip = input("Masukkan IP Server: ").strip()
server_port = int(input("Masukkan Port Server: ").strip())

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# -------------- MUAT DATA USER --------------------
users = load_users()

# ----------------- AUTENTIKASI --------------------
if authenticate_server():  
    main_menu()

    # Mulai thread untuk mengirim dan menerima pesan
    send_thread = threading.Thread(target=send_message)
    receive_thread = threading.Thread(target=receive_message)

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()
