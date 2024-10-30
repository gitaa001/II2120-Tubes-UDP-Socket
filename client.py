import socket
import threading
import csv
import os

# --------------- READ DATA USER -----------------
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

# ---------------- SAVE DATA USER ------------------
def save_user(username, password, filename='users.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

# KIRIM PERAN KE SERVER
def send_message():
    while True:
        try:
            data = input()  #pesan dari user
            if data.lower() == "logout":
                logout()
                break

            message = f"{data}" 
            client_socket.sendto(message.encode(), (server_ip, server_port))
        except KeyboardInterrupt:
            logout()
            break

# TERIMA PESAN DARI SERVER
def receive_message():
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            message = data.decode()
            print(message)  
        except Exception as e:
            print(f"LOG: Error - {e}")
            break

# LOGOUT
def logout():
    logout_message = f"LOGOUT:{username}"
    client_socket.sendto(logout_message.encode(), (server_ip, server_port))
    print("Keluar dari chat.")
    client_socket.close()
    os._exit(0)

# Input server IP, Port, dan Password untuk masuk ke server
server_ip = input("Masukkan IP Server: ").strip()
server_port = int(input("Masukkan Port Server: ").strip())

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    password = input("Masukkan password chatroom: ").strip()
    auth_message = f"AUTH:{password}"
    client_socket.sendto(auth_message.encode(), (server_ip, server_port))

    response, _ = client_socket.recvfrom(1024)
    if response.decode() == "AUTH_SUCCESS":
        print("Berhasil terhubung ke server!")
        break
    else:
        print("Password salah, coba lagi.")

users = load_users() 

# ----------------- MENU UTAMA ------------------
while True:
    print("\n============= MENU ==============")
    print("1. Login\n2. Register\n3. Ketik 'exit' untuk keluar\n")
    action = input(">> Pilih opsi: ").strip()

    if action == '1': #LOGIN
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if not username or not password:
            print("Username dan password tidak boleh kosong. Coba lagi!")
            continue

        if username not in users or users[username] != password:
            print("Username atau password salah. Coba lagi!")
            continue

        # Kirim pesan login ke server
        login_message = f"LOGIN:{username}"
        client_socket.sendto(login_message.encode(), (server_ip, server_port))

        response, _ = client_socket.recvfrom(1024)
        if response.decode() == "Login berhasil.":
            print("\nBerhasil login! Silakan ketik 'logout' jika ingin meninggalkan percakapan.")
            print(">> Mulai mengirim pesan:\n")
            break
        else:
            print(response.decode())

    elif action == '2': #REGISTER
            username = input("Username baru: ").strip()
            password = input("Password baru: ").strip()

            if not username or not password:
                print("Username dan password tidak boleh kosong.")
                continue

            if username in users:
                print("Username sudah terdaftar. Gunakan username lain.")
            else:
                save_user(username, password)
                print("Registrasi berhasil! Silakan login.")
                users[username] = password
                break

    elif action.lower == 'exit':
        print("Terima kasih sudah mencoba layanan kami. Sampai jumpa!")
        exit()

    else:
        print("Pilihan tidak valid.")

# Mulai thread untuk mengirim dan menerima pesan
send_thread = threading.Thread(target=send_message)
receive_thread = threading.Thread(target=receive_message)

send_thread.start()
receive_thread.start()

send_thread.join()
receive_thread.join()
