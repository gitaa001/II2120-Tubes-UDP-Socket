# II2120 - Jaringan Komputer 2024
> Tugas UDP Socket Programming - II2120 Jaringan Komputer 2024
> Dosen: Hamonangan Situmorang, S.T. M.T.

# About
UDP-Based Roomchat ini adalah program jaringan komunikasi sederhana yang dibuat berbasis UDP protocol. Dibuat dalam rangka memenuhi "Tugas UDP Socket Programming".

# Contributors
Khairunnisa Azizah (18223117)
Anggita Najmi Layali (18223122) 

# Features
Program ini berisi fungsi Server dan Client yang menjalankan fungsi masing-masing, di mana peran client dapat diduplikasi (lebih dari satu client dalam server). Tersedia pula users.csv untuk menampung data sebagai alat autentikasi sehingga tiap client yang ingin terhubung dengan server harus memiliki akun dengan username yang unik.

# How to Run
1. Cek ipaddress dengan melakukan "ipconfig" pada terminal.
2. Jalankan server dengan memanggil "python server.py" pada terminal. Input ipaddress yang sesuai dengan ip device server, input port (sembarang).
3. Jalankan client.py dengan memanggil "python client.py" pada terminal. Input ipaddress dan port yang sama dengan server.
4. Input password khusus chatroom yang telah di-set secara hardcore di "server.py".
Selamat mencoba!
