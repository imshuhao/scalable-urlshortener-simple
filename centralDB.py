#!/usr/bin/python3

import socket, time, json, sqlite3, threading, os
from config import *

_cached_stamp = os.stat(propertyFilePath).st_mtime
centralDatabasePath = dbRootPath + "central.db"
lock = threading.Lock()
allMaps = []
databaseContent = {}

def partition():
    global allMaps, _cached_stamp, hosts
    _cached_stamp = os.stat(propertyFilePath).st_mtime
    allMaps.clear()
    for _ in hosts:
        allMaps.append({})
    for k, v in databaseContent.items():
        i = machine_index(k, len(hosts))
        allMaps[i][k] = v
    print("=== Partition Stats ===")
    for i, name in enumerate(hosts):
        print(name, len(allMaps[i]))
    print("========= EOF ========")

# con = sqlite3.connect(dbPath)
con = sqlite3.connect(centralDatabasePath)
cur = con.cursor()
res = cur.execute("SELECT short, long FROM urlMap")
for shortR, longR in res.fetchall():
    databaseContent[shortR] = longR
con.close()
print("[DB] Database loaded.")

partition()

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.2)

def hb():
    while True:
        server.sendto(str.encode(socket.gethostname()+":1\n"), ('<broadcast>', 37021))
        time.sleep(1.5)

configLoader = threading.Thread(target=hb)
configLoader.setDaemon(True)
configLoader.start()

while True:
    stamp = os.stat(propertyFilePath).st_mtime
    if (stamp != _cached_stamp):
        print("[config] Property file changed!")
        readConfig()
        partition()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((socket.gethostname(), tcpPort))
    s.listen()
    conn, addr = s.accept()
    with conn:
        clientHost = socket.gethostbyaddr(addr[0])[0].strip().split(".")[0]
        if clientHost not in hosts:
            s.close()
        machine = hosts.index(clientHost)
        map2send = allMaps[machine]
        print(f"[send] Connected by {addr}, hostname: {clientHost}")
        conn.sendall(json.dumps(map2send).encode('utf-8'))
        print("[send] sent")
    s.close()
    print("[send] Sleeping...")
    time.sleep(10)
