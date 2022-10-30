#!/usr/bin/python3

import socket, time, json, sqlite3, threading, os, random, urllib.request
from config import *


ip2host = {
    "142.1.46.60": "dh2020pc26",
    "142.1.46.61": "dh2020pc27",
    "142.1.46.62": "dh2020pc28",
    "142.1.46.63": "dh2020pc29",
    "142.1.46.64": "dh2020pc30",
}


_cached_stamp = os.stat(propertyFilePath).st_mtime
centralDatabasePath = dbRootPath + "central.db"
allMaps = []
databaseContent = {}

lock = threading.Lock()

running = threading.Event()
running.set()

_bak_hosts, _bak_ports = [], []

def backupHosts():
    global hosts, ports, _bak_hosts, _bak_ports
    _bak_hosts.clear()
    _bak_ports.clear()
    _bak_hosts.extend(hosts)
    _bak_ports.extend(ports)

backupHosts()

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
            print("[CentralDB save] Save failed! Deleting DB file...")
            print("[CentralDB save]", e)
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

def heartbeat():
    while True:
        server.sendto(str.encode(socket.gethostname()+":1\n"), ('<broadcast>', 37021))
        time.sleep(1.5)

configLoader = threading.Thread(target=heartbeat)
configLoader.setDaemon(True)
configLoader.start()

while True:
    try:
        _tmp_hosts, _tmp_ports = [], []
        for i in range(len(_bak_hosts)):
            if isAlive(_bak_hosts[i]):
                _tmp_hosts.append(_bak_hosts[i])
                _tmp_ports.append(_bak_hosts[i])
        if len(_tmp_hosts) != len(hosts):
            hosts.clear()
            ports.clear()
            hosts.extend(_tmp_hosts)
            ports.extend(_tmp_ports)
            print("[CentealDB] Alive hosts updated, re-partitioning...")
            partition()

        stamp = os.stat(propertyFilePath).st_mtime
        if (stamp != _cached_stamp):
            print("[CentralDB] Property file changed!")
            readConfig()
            partition()
            backupHosts()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", tcpPort))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print("[addr]", addr)
            clientHost = ip2host.get(addr[0], '')
            if not clientHost:
                clientHost = socket.gethostbyaddr(addr[0])[0].strip().split(".")[0]
            if clientHost not in hosts:
                s.close()
                continue
            machine = hosts.index(clientHost)
            map2send = allMaps[machine]
            print(f"[CentralDB] Connected by {addr}, hostname: {clientHost}")
            conn.sendall(json.dumps(map2send).encode('utf-8'))
            print("[CentralDB] Partition sent.")
        s.close()
    except KeyboardInterrupt:
        try:
            running.clear()
            s.close()
        except:
            pass
        exit(0)
    except Exception as e:
        print(e)
    time.sleep(0.1)
