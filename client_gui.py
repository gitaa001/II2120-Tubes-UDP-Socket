#client.py
import socket
import threading
import csv
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

class ChatClient:
    def authenticate_server(self):
        """Authenticate with the server before accessing chat functions."""
        password = simpledialog.askstring("Password", "Masukkan password chatroom:", show="*")
        if not password:
            return False
        
        auth_message = f"AUTH:{password}"
        self.client_socket.sendto(auth_message.encode(), (self.server_ip, self.server_port))

        response, _ = self.client_socket.recvfrom(1024)
        if response.decode() == "AUTH_SUCCESS":
            messagebox.showinfo("Success", "Berhasil terhubung ke server!")
            return True
        else:
            messagebox.showerror("Error", "Password salah, coba lagi.")
            return False
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = None
        self.username = ""
        self.is_logged_in = False
        self.users = self.load_users()
        self.stop_event = threading.Event()
        self.create_gui()

    def load_users(self, filename='users.csv'):
        users = {}
        if os.path.exists(filename):
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    username, password = row
                    users[username] = password
        return users

    def save_user(self, username, password, filename='users.csv'):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, password])

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Chat Client")
        
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack()

        # Login frame
        self.login_frame = tk.Frame(self.root)
        self.username_entry = tk.Entry(self.login_frame, width=20)
        self.password_entry = tk.Entry(self.login_frame, show="*", width=20)
        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry.pack()
        tk.Label(self.login_frame, text="Password:").pack()
        self.password_entry.pack()
        tk.Button(self.login_frame, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.login_frame, text="Register", command=self.register).pack(pady=5)

        # Chat frame
        self.chat_frame = tk.Frame(self.root)
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, width=50, height=20, state='disabled')
        self.chat_display.pack()
        self.message_entry = tk.Entry(self.chat_frame, width=50)
        self.message_entry.pack()
        self.message_entry.bind("<Return>", lambda event: self.send_message_gui())
        tk.Button(self.chat_frame, text="Logout", command=self.logout).pack(pady=5)

        self.show_login_frame()

    def show_login_frame(self):
        self.chat_frame.pack_forget()
        self.login_frame.pack()

    def show_chat_frame(self):
        self.login_frame.pack_forget()
        self.chat_frame.pack()

    def send_message_gui(self):
        message = self.message_entry.get()
        if message:
            if message.lower() == "logout":
                self.logout()
            else:
                self.client_socket.sendto(message.encode(), (self.server_ip, self.server_port))
                self.message_entry.delete(0, tk.END)

    def receive_message(self):
        while self.is_logged_in:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                message = data.decode()
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, message + "\n")
                self.chat_display.config(state='disabled')
                self.chat_display.see(tk.END)
            except Exception as e:
                if self.stop_event.is_set():
                    break

    def logout(self):
        if self.is_logged_in:
            logout_message = f"LOGOUT:{self.username}"
            self.client_socket.sendto(logout_message.encode(), (self.server_ip, self.server_port))
            self.is_logged_in = False
            self.stop_event.set()
            self.client_socket.close()
            self.show_login_frame()

    def authenticate_server(self):
        password = tk.simpledialog.askstring("Password", "Masukkan password chatroom:", show="*")
        if password:
            auth_message = f"AUTH:{password}"
            self.client_socket.sendto(auth_message.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response.decode() == "AUTH_SUCCESS":
                return True
            else:
                messagebox.showerror("Error", "Password salah, coba lagi.")
        return False

    def login(self):
        self.username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.username not in self.users:
            messagebox.showerror("Error", "Username belum terdaftar. Silakan register.")
            return

        if self.users[self.username] != password:
            messagebox.showerror("Error", "Password salah. Coba lagi.")
            return

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        if not self.authenticate_server():
            return

        login_message = f"LOGIN:{self.username}"
        self.client_socket.sendto(login_message.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        if response.decode() == "Login berhasil.":
            self.is_logged_in = True
            self.show_chat_frame()
            threading.Thread(target=self.receive_message, daemon=True).start()
        else:
            messagebox.showerror("Error", response.decode())

    def register(self):
        new_username = self.username_entry.get().strip()
        new_password = self.password_entry.get().strip()

        if not new_username or not new_password:
            messagebox.showerror("Error", "Username dan password tidak boleh kosong.")
            return

        if new_username in self.users:
            messagebox.showerror("Error", "Username sudah terdaftar. Gunakan username lain.")
        else:
            self.save_user(new_username, new_password)
            self.users[new_username] = new_password
            messagebox.showinfo("Info", "Registrasi berhasil! Silakan login.")

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.logout)
        self.root.mainloop()


# Run Client
server_ip = input("Masukkan IP Server: ").strip()
server_port = int(input("Masukkan Port Server: ").strip())
client = ChatClient(server_ip, server_port)
client.start()
