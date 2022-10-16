#!/usr/bin/python3

import random, string, subprocess

for i in range(10000):
	request="http://localhost:8080/000000000000000000000000000000000000000000000"
	# print(request)
	subprocess.call(["curl", "-X", "GET", request], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
