#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import threading, socket, time, sqlite3, urllib.parse, json, random, os
from config import *
import sys

lock = threading.Lock()
urlMap = {}
running = True


def save():
    while running:
        sleepTime = random.randint(10, 20)
        print(f"[save] Sleeping for {sleepTime} seconds...")
        time.sleep(sleepTime)
        try:
            lock.acquire()
            items = list(urlMap.items())
            lock.release()
            con = sqlite3.connect(dbPath)
            cur = con.cursor()
            con.execute('''create table if not exists urlMap (short varchar(50) primary key, long varchar(150) not null);''')
            cur.executemany("INSERT OR IGNORE INTO urlMap(short, long) VALUES(?, ?)", items)
            con.commit()
            con.close()
            print("[save] saved, sleeping...")
        except:
            removeDatabaseFile()

def sync():
    global urlMap
    while running:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((dbCentralHostname, tcpPort))
                # s.sendall(b"Hello, world")
                res = b""
                while running:
                    data = s.recv(1024000000)
                    if not data:
                        break
                    res += data
                    print(f"[sync] Received {sys.getsizeof(data)} bytes.")
                entries = json.loads(res.decode('UTF-8'))
                res = b""
                lock.acquire()
                urlMap.clear()
                urlMap.update(entries)
                lock.release()
                print("[sync] urlMap updated!")
        except KeyboardInterrupt:
            # lock.release()
            exit(1)
        except Exception as e:
            # lock.release()
            print(e)
        sleepTime = random.randint(30, 50)
        print(f"[sync] Sleeping for {sleepTime} seconds...")
        time.sleep(sleepTime)


class URLShortner:
    def __init__(self, port, dbPath):
        global urlMap
        self.hostname = "0.0.0.0"
        self.port = port
        try:
            con = sqlite3.connect(dbPath)
            cur = con.cursor()
            res = cur.execute("SELECT short, long FROM urlMap")
            for shortR, longR in res.fetchall():
                urlMap[shortR] = longR
            con.close()
        except:
            removeDatabaseFile()
    
    def serve(self):
        server = ThreadingHTTPServer((self.hostname, self.port), Handler)
        print("[URLShotner] Server started http://%s:%s" % (self.hostname, self.port))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        
        server.server_close()
        print("[URLShotner] Server stopped.")
        global running
        running = False
        #self.save()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global urlMap
        shortURL = self.path[1:]
        if not shortURL:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "r") as f:
                html = f.read()
                self.wfile.write(str.encode(html))
                return
        longURL = urlMap.get(shortURL)
        if longURL:
            self.send_response(307)
            self.send_header("Content-type", "text/html")
            self.send_header("Location", longURL)
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>Moved</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Moved</h1><p>This page has moved</p></body></html>", "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>Not Found</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Not Found</h1></body></html>", "utf-8"))
    
    def do_PUT(self):
        global urlMap
        global lock
        path = urllib.parse.unquote(self.path[2:])
        data = path.strip().split("&")
        shortURL = data[0].split("=")[1]
        longURL = data[1].split("=")[1]
        if shortURL and longURL:
            lock.acquire()
            urlMap[shortURL] = longURL
            lock.release()
            self.send_response(201)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>Success</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Success</h1></body></html>", "utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<html><head><title>Bad Request</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Bad Request</h1></body></html>", "utf-8"))


if __name__ == "__main__":
    saveT = threading.Thread(target=save)
    saveT.start()
    syncT = threading.Thread(target=sync)
    syncT.start()
    app = URLShortner(serverPort, dbPath)
    app.serve()