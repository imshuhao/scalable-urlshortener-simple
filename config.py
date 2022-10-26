import os, hashlib, socket, pwd, pathlib

propertyFilePath = "config.properties"
cached_stamp = 0
utorid = pwd.getpwuid(os.getuid()).pw_name



### === Helper Functions ===
machine_index = lambda x, y : int.from_bytes(hashlib.md5(x.encode('utf-8')).digest()[0:1], "big") % y

def removeDatabaseFile():
    try:
        os.remove(dbPath)
    except FileNotFoundError:
        pass


### ==== Default Config Variables ===
serverPort = 0
tcpPort = 0
dbPath = f"/virtual/{utorid}/URLShortner/urlMap.db"
dbRootPath = f"/virtual/{utorid}/URLShortner/"
dbCentralHostname = ""
hosts = []

propertyFile = {}


pathlib.Path(dbRootPath).mkdir(parents=True, exist_ok=True)


### === Reading Java .properties File ===
def readConfig():
    global hosts, dbPath, tcpPort, dbCentralHostname, serverPort
    propertyFile.clear()
    with open(propertyFilePath, "r") as f:
        for line in f:
            try:
                k, v = line.strip().split(":")
            except ValueError:
                break
            propertyFile[k] = v

    dbPath = propertyFile["SQLite"]
    tcpPort = int(propertyFile["tcpPort"])
    dbCentralHostname = propertyFile["dbCentralHost"]
    hosts.clear()
    for i in range(100000):
        try:
            h, p = propertyFile[f"hostname{i}"], propertyFile[f"port{i}"]
        except KeyError:
            break
        hosts.append(h)
        if h == socket.gethostname():
            serverPort = int(p)

readConfig()
