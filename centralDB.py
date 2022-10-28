#!/usr/bin/python3

import socket, time, json, sqlite3, threading, os, random, urllib.request
from config import *

_cached_stamp = os.stat(propertyFilePath).st_mtime
centralDatabasePath = dbRootPath + "central.db"
allMaps = []
databaseContent = {}

lock = threading.Lock()

running = threading.Event()
running.set()


def save():
    global databaseContent
    while running.is_set():
        if not databaseContent:
            time.sleep(5)
            continue
        sleepTime = random.randint(30, 50)
        print(f"[CentralDB save] Sleeping for {sleepTime} seconds...")
        time.sleep(sleepTime)
        try:
            with lock:
                items = list(databaseContent.items())
            con = sqlite3.connect(centralDatabasePath)
            cur = con.cursor()
            con.execute('''create table if not exists urlMap (short varchar(50) primary key, long varchar(150) not null);''')
            cur.executemany("INSERT OR IGNORE INTO urlMap(short, long) VALUES(?, ?)", items)
            con.commit()
            con.close()
            print("[CentralDB save] Saved to database (central.db).")
        except Exception as e:
            print(e)
            print("[CentralDB save] Save failed! Deleting DB file...")
            removeDatabaseFile(centralDatabasePath)


def pull_data():
    global databaseContent
    while running.is_set():
        sleepTime = random.randint(60, 90)
        print(f"[CentralDB pull] Sleeping for {sleepTime} seconds...")
        time.sleep(sleepTime)
        tempMap = {}
        for i in range(len(hosts)):
            try:
                contents = urllib.request.urlopen(f"http://{hosts[i]}:{ports[i]}/givemedata").read()
            except:
                continue
            tempMap = json.loads(contents)
            print(f"[CentralDB pull] Successfully pulled {len(tempMap)} entries from {hosts[i]}")
            with lock:
                databaseContent.update(tempMap)
            print(f"[CentralDB pull] DB cache updated.")

saveT = threading.Thread(target=save)
saveT.start()
pullT = threading.Thread(target=pull_data)
pullT.start()


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
print("[CentralDB] Database loaded.")

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
    try:
        stamp = os.stat(propertyFilePath).st_mtime
        if (stamp != _cached_stamp):
            print("[CentralDB] Property file changed!")
            readConfig()
            partition()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((socket.gethostname(), tcpPort))
        s.listen()
        conn, addr = s.accept()
        with conn:
            clientHost = socket.gethostbyaddr(addr[0])[0].strip().split(".")[0]
            machine = hosts.index(clientHost)
            map2send = allMaps[machine]
            print(f"[CentralDB] Connected by {addr}, hostname: {clientHost}")
            conn.sendall(json.dumps(map2send).encode('utf-8'))
            print("[CentralDB] Partition sent.")
        s.close()
    except KeyboardInterrupt:
        try:
            s.close()
        except:
            pass
        running.clear()
        exit(0)
    except Exception as e:
        print(e)
    print("[CentralDB] Sleeping for 10 seconds before next send...")
    time.sleep(10)