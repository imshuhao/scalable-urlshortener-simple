#!/usr/bin/python3

import random, string, subprocess

import time
import curses
hosts = ["dh2020pc18", "localhost"]

# for host in hosts:
#     request = host + ":8080/arnold"
# 	# print(request)
# 	# p = subprocess.run(["curl", "-X", "GET", request], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-X", "GET", "-w", "%{http_code}", request], capture_output=True, text=True)
#     if(p.stdout != "307" and p.stdout!= "404"):
#         print(host + " is down")


def pbar(window):
    while True:
        offsetY = 0
        for host in hosts:
            request = host + ":8080/arnold"
            p = subprocess.run(["curl", "-s", "-o", "/dev/null", "-X", "GET", "-w", "%{http_code}", request], capture_output=True, text=True)
            status = "O"
            if(p.stdout != "307" and p.stdout!= "404"):
                status = "X"
            window.addstr(offsetY, 0, "[" + status + "] " + host)
            offsetY += 2
        # window.addstr(10, 10, "[" + ("=" * i) + ">" + (" " * (10 - i )) + "]")
        window.refresh()
        time.sleep(1)

curses.wrapper(pbar)
