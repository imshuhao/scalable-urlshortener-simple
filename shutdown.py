#!/usr/bin/python3
import os,sys, socket

dir_path = os.path.dirname(os.path.realpath(__file__))


with open("config.properties", "r") as f:
    raw = f.readlines()
prop = {}
for line in raw:
    k, v = line.strip().split(":")
    prop[k] = v

for k,v in prop.items():
    if not k.startswith("hostname") or v == socket.gethostname():
        continue
    os.system(f"ssh {v} 'pkill py'")

if socket.gethostname() in prop.values():
    os.system("pkill py")
