#!/usr/bin/python3

import random, string, subprocess, os

import time
import curses
# import socket
import threading

dir_path = os.path.dirname(os.path.realpath(__file__))

hosts = []

# server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# server.settimeout(0.2)

# client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
# client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# client.settimeout(0.2)
# client.bind(("", 37021))


def monitor(window):
    try:
        while True:
            statusString = ""
            for host, port in hosts:
                request = host + f":{port}/arnold"
                p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-X", "GET", "-w", "%{http_code}", request], capture_output=True, text=True)
                alive = True if p.stdout == "307" or p.stdout== "404" else False
                statusString += host + (":1" if alive else ":0") + "\n"

                if not alive:
                    revive(host)
            f = open("status.properties", "w")
            f.write(statusString)
            f.close()
            # print(statusString)
            render(window, statusString)

            time.sleep(2)
            # try:
            #     data, addr = client.recvfrom(1024)
            # except socket.timeout:
            #     server.sendto(str.encode(statusString), ('<broadcast>', 37021))
    except KeyboardInterrupt:
        os.system("python3 ./shutdown.py")
        exit(1)

def render(window, s):
    window.addstr(0, 0, s)
    window.refresh()

def revive(host):
    # os.system("pkill java && ./run.bash")
    os.system(f"ssh {host} 'pkill python3; cd {dir_path}; python3 ./PythonImplementation/URLShortner.py' &")

def loadConfig():
    while True:
        global hosts
        prop = {}
        new_hosts = []
        with open("config.properties", "r") as f:
            raw = f.readlines()

        for line in raw:
            k, v = line.strip().split(":")
            prop[k] = v

        for i in range(100000000000):
            host = prop.get(f"hostname{i}", None)
            port = prop.get(f"port{i}", None)
            if host is None or port is None:
                break
            new_hosts.append((host, port))
        hosts = new_hosts

        time.sleep(10)

def main(window):
    configLoader = threading.Thread(target=loadConfig)
    configLoader.setDaemon(True)
    configLoader.start()
    time.sleep(1)
    monitor(window)

curses.wrapper(main)
