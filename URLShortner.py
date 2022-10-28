#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import threading, socket, time, sqlite3, urllib.parse, json, random, os, sys
from config import *


index_html = ""
with open("index.html", "r") as f:
    index_html = f.read()
lock = threading.Lock()
urlMap = {}
running = threading.Event()
running.set()

def save():
    while running.is_set():
        sleepTime = random.randint(10, 20)
        print(f"[save] Sleeping for {sleepTime} seconds...")
        time.sleep(sleepTime)
        try:
            with lock:
                items = list(urlMap.items())
            con = sqlite3.connect(dbPath)
            cur = con.cursor()
            con.execute('''create table if not exists urlMap (short varchar(50) primary key, long varchar(150) not null);''')
            cur.executemany("INSERT OR IGNORE INTO urlMap(short, long) VALUES(?, ?)", items)
            con.commit()
            con.close()
            print(f"[save] Saved to host database with {len(items)} entries.")
        except KeyboardInterrupt:
            exit(0)
        except:
            removeDatabaseFile(dbPath)

def sync():
    global urlMap
    while running.is_set():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((dbCentralHostname, tcpPort))
                # s.sendall(b"Hello, world")
                res = b""
                while running.is_set():
                    data = s.recv(1024000000)
                    if not data:
                        break
                    res += data
                    print(f"[sync] {socket.gethostname()} received {sys.getsizeof(data)} bytes.")
                entries = json.loads(res.decode('UTF-8'))
                res = b""
                lock.acquire()
                urlMap.clear()
                urlMap.update(entries)
                lock.release()
                print(f"[sync] {socket.gethostname()} urlMap updated!")
                with lock:
                    urlMap.clear()
                    urlMap.update(entries)
                print("[sync] urlMap updated!")
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print(e)
        sleepTime = random.randint(30, 50)
        print(f"[sync] {socket.gethostname()} sleeping for {sleepTime} seconds...")
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
            removeDatabaseFile(dbPath)
    
    def serve(self):
        server = ThreadingHTTPServer((self.hostname, self.port), Handler)
        print("[URLShotner] Server started http://%s:%s" % (socket.gethostname(), self.port))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        
        server.server_close()
        print("[URLShotner] Server stopped.")
        running.clear()
        # global running
        # running = False
        #self.save()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global urlMap, index_html
        shortURL = self.path[1:]
        if not shortURL:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(str.encode(index_html))
            return
        if shortURL == "givemedata":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(urlMap).encode('utf-8'))
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
            with lock:
                urlMap[shortURL] = longURL
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