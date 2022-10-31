#!/usr/bin/python3

import random, string, subprocess
import urllib.request


host = "http://dh2020pc29:8086/"

for i in range(1000):
    if i % 10 == 0:
        print(i)
    longResource = "http://"+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))
    shortResource = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
    request = host + "?short=" + shortResource + "&long=" + longResource
    subprocess.call(["curl", "-X", "PUT", request], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    res = subprocess.check_output(["curl", "-X", "GET", host+shortResource], stderr=subprocess.DEVNULL)
    # print(res)
    if b'Moved' not in res:
        print("error", shortResource, longResource)
