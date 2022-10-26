#!/usr/bin/python3

import random, string, subprocess, os

import time
import curses
# import socket
import threading

dir_path = os.path.dirname(os.path.realpath(__file__))

hosts = []
proxyHost = None
proxyPort = None

# server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# server.settimeout(0.2)

# client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
# client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# client.settimeout(0.2)
# client.bind(("", 37021))

# TODO: revive proxy, terminate proxy on exit
def monitor(window):
    try:
        while True:
            statusString = ""
            if proxyHost and proxyPort:
                request = proxyHost + f":{proxyPort}/hb"
                p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-X", "GET", "-w", "%{http_code}", request], capture_output=True, text=True)
                proxyAlive = True if p.stdout == "200" else False
                statusString += proxyHost + (":1" if proxyAlive else ":0") + " (proxy)" +"\n"

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
            render(window, statusString)

            time.sleep(2)
            # try:
            #     data, addr = client.recvfrom(1024)
            # except socket.timeout:
            #     server.sendto(str.encode(statusString), ('<broadcast>', 37021))
    except KeyboardInterrupt:
        os.system("python3 ./shutdown.py")
        if proxyHost:
            os.system(f"ssh {proxyHost} 'pkill java'")
        exit(1)

def render(window, s):
    window.clear()
    window.addstr(0, 0, s)
    window.refresh()

def revive(host):
    # os.system("pkill java && ./run.bash")
    loadConfig(False)
    if any([host in host_pair for host_pair in hosts]):
        os.system(f"ssh {host} 'pkill python3; cd {dir_path}; python3 ./PythonImplementation/URLShortner.py' &")

def revive_proxy(host):
    os.system(f"ssh {host} 'pkill python3; cd {dir_path}; python3 ./PythonImplementation/URLShortner.py' &")


def loadConfig(fromThread):
    while True:
        global hosts
        global proxyHost
        global proxyPort
        prop = {}
        new_hosts = []
        with open("config.properties", "r") as f:
            raw = f.readlines()

        for line in raw:
            k, v = line.strip().split(":")
            prop[k] = v

        proxyHost = prop.get("proxyHost", None)
        proxyPort = prop.get("proxyPort", None)

        for i in range(100000000000):
            host = prop.get(f"hostname{i}", None)
            port = prop.get(f"port{i}", None)
            if host is None or port is None:
                break
            new_hosts.append((host, port))
        hosts = new_hosts

        if fromThread:
            time.sleep(10)
        else:
            return

def main(window):
    configLoader = threading.Thread(target=loadConfig, args=(True,))
    configLoader.setDaemon(True)
    configLoader.start()
    time.sleep(1)
    monitor(window)

curses.wrapper(main)
# main(1)
