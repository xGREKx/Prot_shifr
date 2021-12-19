import socket, random, threading, csv

def encrypt(k, m):
    return ''.join(map(chr, [(x + k) % 65536 for x in map(ord, m)]))

def decrypt(k, c):
    return ''.join(map(chr, [(x - k) % 65536 for x in map(ord, c)]))

def listening(sock):
    global private_key
    while True:
        msg = sock.recv(1024).decode()
        msg = decrypt(private_key, msg)
        print(msg)

def read_keys():
    global addr
    with open("server_key.csv", "r", newline = "") as keyfile:
        reader = csv.reader(keyfile, delimiter = ";")
        for row in reader:
            if row[0] == addr[0]:
                return row[1:] #a,g,p,A,B,H
        else:
            raise FileNotFoundError

def get_keys():
    global conn, addr
    try:
        keys = read_keys()
    except FileNotFoundError:
        a, g, p = [random.randint(100,999) for _ in range(3)]
        my_a = pow(g, a) % p
        conn.send(f"{g}|{p}|{my_a}".encode())
        cli_b = int(conn.recv(1024).decode())
        private = pow(cli_b, a) % p
        keys = [a, g, p, my_a, cli_b, private]
        with open("server_key.csv", "w", newline = "") as keyfile:
            writer = csv.writer(keyfile, delimiter = ";")
            writer.writerow((addr[0], *keys))
    else:
        keys = [int(item) for item in keys]
        conn.send(f"{keys[1]}|{keys[2]}|{keys[3]}".encode())
        cli_b = int(conn.recv(1024).decode())
    return keys[5], cli_b


def check_permission(cli_b):
    with open("allowed.csv", "r", newline = "") as keyfile:
        reader = csv.reader(keyfile, delimiter = ";")
        for row in reader:
            if int(row[0]) == cli_b:
                return True
        else:
            return False

def create_socket(port = 10101):
    sock = socket.socket()
    sock.setblocking(True)
    sock.bind(('', port))
    print(f"Socket binded at port {port}")
    sock.listen(0)
    conn, addr = sock.accept()
    return sock, conn, addr

def messaging_port():
    global sock, conn, private_key
    port = random.randint(1024,65535)
    conn.send(encrypt(private_key, str(port)).encode())
    sock.close()
    return create_socket(port)



sock, conn, addr = create_socket()
private_key, client_b = get_keys() 


if check_permission(client_b):
# if True:
    sock, conn, addr = messaging_port()
    threading.Thread(target = listening, args = (conn, ), daemon = True).start() 
    while True:
        cmd = input()
        if cmd == "stop":
            break
        cmd = encrypt(private_key, cmd)
        conn.send(cmd.encode())
else:
    print("Неизвестный сертификат клиента")
sock.close()