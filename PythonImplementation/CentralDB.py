import socket, time, json, sqlite3, threading
from config import *

lock = threading.Lock()
allMaps = []

for _ in hosts:
    allMaps.append({})

# con = sqlite3.connect(dbPath)
con = sqlite3.connect("urlMap.db")
cur = con.cursor()
res = cur.execute("SELECT short, long FROM urlMap")
for shortR, longR in res.fetchall():
    machine = partition(shortR, len(hosts))
    allMaps[machine][shortR] = longR
con.close()

for i, name in enumerate(hosts):
    print(name, len(allMaps[i]))

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((socket.gethostname(), tcpPort))
    s.listen()
    conn, addr = s.accept()
    with conn:
        clientHost = socket.gethostbyaddr(addr[0])[0].strip().split(".")[0]
        machine = hosts.index(clientHost)
        map2send = allMaps[machine]
        print(f"[Send] Connected by {addr}, hostname: {clientHost}")
        conn.sendall(json.dumps(map2send).encode('utf-8'))
        print("[Send] sent")
    s.close()
    print("[send] Sleeping...")
    time.sleep(10)
