#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import threading, time, sqlite3, urllib.parse
from config import *

lock = threading.Lock()
urlMap = {}
running = True


def save():
    while running:
        time.sleep(10)
        lock.acquire()
        # print("lock acquired")
        items = list(urlMap.items())
        lock.release()
        # print("lock released")
        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        cur.executemany("INSERT OR IGNORE INTO urlMap(short, long) VALUES(?, ?)", items)
        con.commit()
        con.close()
        print("saved, sleeping...")

def sync():
    pass



class URLShortner:
    def __init__(self, hostname, port, dbPath):
        global urlMap
        self.hostname = hostname
        self.port = port
        con = sqlite3.connect(dbPath)
        cur = con.cursor()
        res = cur.execute("SELECT short, long FROM urlMap")
        for shortR, longR in res.fetchall():
            urlMap[shortR] = longR
        con.close()
    
    def serve(self):
        server = ThreadingHTTPServer((self.hostname, self.port), Handler)
        print("Server started http://%s:%s" % (self.hostname, self.port))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        
        server.server_close()
        print("Server stopped.")
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
        # print(f"Short: {shortURL}, Long: {longURL}")
        
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
        # print(shortURL, longURL)
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
    x = threading.Thread(target=save)
    x.start()
    app = URLShortner(hostName, serverPort, dbPath)
    app.serve()