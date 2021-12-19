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
    global sock
    with open("client_key.csv", "r", newline = "") as keyfile:
        reader = csv.reader(keyfile, delimiter = ";")
        return [int(item) for item in next(reader)]

def get_keys():
    global sock
    server_keys = sock.recv(1024).decode().split("|")#g, p, A
    server_keys = [int(item) for item in server_keys]
    try:
        keys = read_keys()
    except FileNotFoundError:
        b = random.randint(100,999)
        g = server_keys[0]
        p = server_keys[1]
        my_b = pow(g, b) % p
        serv_a = server_keys[2]
        private = pow(serv_a, b) % p
        keys = [b, g, p, my_b, serv_a, private]
        with open("client_key.csv", "w", newline = "") as keyfile:
            writer = csv.writer(keyfile, delimiter = ";")
            writer.writerow(keys)
    sock.send(str(keys[3]).encode())
    return keys


sock = socket.socket()
sock.setblocking(True)
sock.connect(('localhost', 10101))
print(f"Socket connected at port 10101")
all_keys = get_keys()
private_key = all_keys[5]
port = int(decrypt(private_key,sock.recv(1024).decode()))
sock.close()
sock = socket.socket()
sock.setblocking(True)
sock.connect(('localhost', port))
print(f"Socket binded at port {port}")
threading.Thread(target = listening, args = (sock, ), daemon = True).start()

while True:
    cmd = input()
    if cmd == "stop":
        break
    cmd = encrypt(private_key, cmd)
    sock.send(cmd.encode())

sock.close()