#!/usr/bin/python3
import os,sys

dir_path = os.path.dirname(os.path.realpath(__file__))


with open("config.properties", "r") as f:
    raw = f.readlines()
prop = {}
for line in raw:
    k, v = line.strip().split(":")
    prop[k] = v

for k,v in prop.items():
    if not k.startswith("hostname"):
        continue
    # print(f"ssh dongshu4@{v} 'bash dir_path/run.bash'")
    os.system(f"ssh {v} 'pkill java; cd {dir_path}; ./run.bash' &")