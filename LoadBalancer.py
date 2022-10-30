#!/usr/bin/python3

from re import T
import socket
import sys
import threading
import time
from config import *

max_connection = 8
buffer_size = 8192
hot_cache = {}

_cached_stamp = os.stat(propertyFilePath).st_mtime

_hosts, _ports = [], []

def syncHosts():
    global hosts, ports, _hosts, _ports
    _hosts.clear()
    _ports.clear()
    _hosts.extend(hosts)
    _ports.extend(ports)

syncHosts()

def monitor_status():
    global _hosts, _ports, _cached_stamp
    while True:
        stamp = os.stat(propertyFilePath).st_mtime
        if (stamp != _cached_stamp):
            print("[LB] Property file changed!")
            readConfig()
            syncHosts()
            # backupHosts()
            _cached_stamp = stamp
        _hosts.clear()
        _ports.clear()
        for i in range(len(hosts)):
            if isAlive(hosts[i]):
                _hosts.append(hosts[i])
                _ports.append(ports[i])
        time.sleep(10)

t_monitor_status = threading.Thread(target=monitor_status, daemon=True)
t_monitor_status.start()


def start():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", proxyPort))
        sock.listen(max_connection)
        print(f"[LB] Server started on http://{socket.gethostname()}:{proxyPort}")
    except Exception as e:
        print("[LB] Unable to Initialize Socket")
        print(e)
        sys.exit(2)

    while True:
        try:
            conn, addr = sock.accept()
            data = conn.recv(buffer_size)
            t = threading.Thread(target=redirect, args=(conn, data, addr), daemon=True)
            t.start()
        except KeyboardInterrupt:
            sock.close()
            print("\n[LB] Keyboard interrupted, exit.")
            sys.exit(1)
        except Exception as e:
            print("[LB]", e)
            sock.close()
            continue

def redirect(conn, data, addr):
    if not data:
        return
    try:
        first_line = data.split(b'\r\n')[0]
        shortResource = first_line.split()[1][1:]
        machine2send = machine_index_bytes(shortResource, len(_hosts))
        target_host, target_port = _hosts[machine2send], _ports[machine2send]
        # print(f"Short: {shortResource}, Target Host: {target_host}:{target_port}")
        forward(target_host, target_port, conn, addr, first_line + b'\r\n\r\n', shortResource)
    except Exception as e:
        print(data, _hosts, _ports, hosts, ports)
        print("[LB redirect]", e)

def forward(host, port, conn, addr, data, shortResource):
    global hot_cache
    if len(hot_cache) > 10000:
        hot_cache.clear()
    if shortResource in hot_cache:
        conn.send(hot_cache[shortResource])
        conn.close()
        # print("[LB forward] cache hit")
        return
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.send(data)

        while True:
            reply = sock.recv(buffer_size)
            if(len(reply) > 0):
                conn.send(reply)
                hot_cache[shortResource] = reply
            else:
                break
        sock.close()
        conn.close()
    except Exception as e:
        sock.close()
        conn.close()
        print("[LB forward]", e)
        sys.exit(1)

if __name__== "__main__":
    start()