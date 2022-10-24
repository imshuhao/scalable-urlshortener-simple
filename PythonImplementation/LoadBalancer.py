#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import threading
import time
import sqlite3
import requests
import urllib.parse

hostName = "localhost"
serverPort = 8081


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        x = requests.get('localhost:8080')
    
    def do_PUT(self):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer((hostName, serverPort), Handler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    print("Server stopped.")