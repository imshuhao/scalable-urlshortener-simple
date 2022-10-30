import os, hashlib, socket, pwd, pathlib

propertyFilePath = "config.properties"
statusFilePath = "status.properties"
cached_stamp = 0
utorid = pwd.getpwuid(os.getuid()).pw_name



### === Helper Functions ===
machine_index = lambda x, y : int.from_bytes(hashlib.md5(x.encode('utf-8')).digest()[0:1], "big") % y

def removeDatabaseFile(p):
    try:
        os.remove(p)
    except FileNotFoundError:
        pass


### ==== Default Config Variables ===
serverPort = tcpPort = proxyPort = 0
dbPath = f"/virtual/{utorid}/URLShortner/urlMap.db"
dbRootPath = f"/virtual/{utorid}/URLShortner/"
dbCentralHostname = ""
hosts, ports = [], []

propertyFile = {}


pathlib.Path(dbRootPath).mkdir(parents=True, exist_ok=True)


def isAlive(host):
    try:
        with open(statusFilePath, 'r') as f:
            for line in f:
                line = line.strip().split(":")
                if line[0] == host:
                    return False if line[1].startswith('0') else True
    except FileNotFoundError:
        return True

### === Reading Java .properties File ===
def readConfig():
    global hosts, dbPath, tcpPort, dbCentralHostname, serverPort, proxyPort
    propertyFile.clear()
    with open(propertyFilePath, "r") as f:
        for line in f:
            try:
                k, v = line.strip().split(":")
            except ValueError:
                break
            propertyFile[k] = v
    tcpPort = int(propertyFile["tcpPort"])
    dbCentralHostname = propertyFile["dbCentralHost"]
    proxyPort = int(propertyFile["proxyPort"])
    hosts.clear()
    for i in range(100000):
        try:
            h, p = propertyFile[f"hostname{i}"], propertyFile[f"port{i}"]
        except KeyError:
            break
        hosts.append(h)
        ports.append(int(p))
        if h == socket.gethostname():
            serverPort = int(p)

readConfig()
