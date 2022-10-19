#!/usr/bin/python3
import subprocess, os

while True:
    os.system("javac SimpleProxyServer.java")
    subprocess.run(["java", "SimpleProxyServer"])