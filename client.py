import socket
import threading
import csv
import os

# Function to load users from CSV
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

# Function to save new user to CSV
def save_user(username, password, filename='users.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])

# Function for user login with validation
def login(users):
    while True:
        username = input("Masukkan username: ").strip()
        password = input("Masukkan password: ").strip()
        
        if not username or not password:
            print("Username dan password tidak boleh kosong. Coba lagi.")
            continue

        if username in users and users[username] == password:
            print("Login berhasil!")
            return username
        else:
            print("Username atau password salah. Coba lagi.")

# Function for user registration with validation
def register(users):
    while True:
        username = input("Masukkan username baru: ").strip()
        if not username:
            print("Username tidak boleh kosong. Coba lagi.")
            continue
        
        if username in users:
            print("Username sudah terdaftar. Coba username lain.")
        else:
            password = input("Masukkan password baru: ").strip()
            if not password:
                print("Password tidak boleh kosong. Coba lagi.")
                continue
            
            save_user(username, password)
            print("Registrasi berhasil!")
            return username

# Input server IP and port with validation
while True:
    IpAddress = input("Masukkan IP Address: ").strip()
    if not IpAddress:
        print("IP Address tidak boleh kosong. Coba lagi.")
        continue

    portServer = input("Masukkan Port Number: ").strip()
    if not portServer.isdigit() or int(portServer) <= 0:
        print("Port Number tidak boleh kosong dan harus berupa angka positif. Coba lagi.")
        continue
    
    clientPort = int(input("Masukkan clientPort: ").strip())
    if clientPort <= 0:
        print("Client port harus berupa angka positif. Coba lagi.")
        continue

    portServer = int(portServer)
    break

# Create a client socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('0.0.0.0', clientPort))  # Bind to all interfaces

# Load existing users from CSV
users = load_users()

# Choose between login or registration
while True:
    action = input("Apa yang kamu mau?\n1. Login\n2. Register\n\nMasukkan angka: ")
    if action == '1':
        username = login(users)
        # Attempt to login
        login_message = f"{username}|dummy"
        clientSocket.sendto(login_message.encode(), (IpAddress, portServer))
        data, _ = clientSocket.recvfrom(1024)
        response = data.decode()
        if response == "Username already logged in.":
            print("Login gagal: Username sudah digunakan.")
            continue
        break
    elif action == '2':
        username = register(users)
        break
    else:
        print("Pilihan tidak valid. Silakan pilih 1 atau 2.")

# Function to send messages to the server
def sendMessage():
    while True:
        data = input("You: ")  # User input
        message = f"{username}|{data}"  # Send username and message
        clientSocket.sendto(message.encode(), (IpAddress, portServer))  # Send message to server

# Function to receive messages from the server
def receiveMessage():
    while True:
        try:
            data, addr = clientSocket.recvfrom(1024)
            message = data.decode()
            sender, chatMessage = message.split("|", 1)

            # Check if the sender is the user themselves
            if sender == username:
                print(f"You: {chatMessage}")
            else:
                print(f"{sender}: {chatMessage}")

        except Exception as e:
            print(f"LOG: Error saat menerima pesan: {e}")
            break

# Start threads for sending and receiving messages
sendThread = threading.Thread(target=sendMessage)
receiveThread = threading.Thread(target=receiveMessage)

sendThread.start()
receiveThread.start()

sendThread.join()
receiveThread.join()

