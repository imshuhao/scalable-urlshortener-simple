import os, hashlib

serverPort = 8848
dbPath = "/virtual/dongshu4/URLShortner/urlMap.db"
tcpPort = 65433
dbCentralHostname = "dh2020pc28"
hosts = ["dh2020pc27", "dh2020pc28", "dh2020pc29", "dh2020pc30"]

partition = lambda x, y : int.from_bytes(hashlib.md5(x.encode('utf-8')).digest()[0:1], "big") % y

def removeDatabaseFile():
    try:
        os.remove(dbPath)
    except FileNotFoundError:
        pass