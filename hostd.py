#!/usr/bin/python3

import random, string, subprocess, os

import time
import curses
import socket

hosts = []
with open("config.properties", "r") as f:
    raw = f.readlines()
prop = {}
for line in raw:
    k, v = line.strip().split(":")
    prop[k] = v

for i in range(100000000000):
    host = prop.get(f"hostname{i}", None)
    port = prop.get(f"port{i}", None)
    if host is None or port is None:
        break
    hosts.append((host, port))

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.settimeout(0.2)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.settimeout(0.2)
client.bind(("", 37021))

def monitor():
    while True:
        statusString = ""
        for host, port in hosts:
            request = host + f":{port}/arnold"
            p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-X", "GET", "-w", "%{http_code}", request], capture_output=True, text=True)
            alive = True if p.stdout == "307" or p.stdout== "404" else False
            statusString += host + (":1" if alive else ":0") + "\n"

            if host == socket.gethostname() and not alive:
                revive()

        time.sleep(1)
        try:
            data, addr = client.recvfrom(1024)
        except socket.timeout:
            server.sendto(str.encode(statusString), ('<broadcast>', 37021))
            print(statusString)

def revive():
    os.system("pkill java && ./run.bash")

while True:
    monitor()