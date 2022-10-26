import sqlite3, os, pwd, pathlib

dbRootPath = f"/virtual/{pwd.getpwuid(os.getuid()).pw_name}/URLShortner/"
pathlib.Path(dbRootPath).mkdir(parents=True, exist_ok=True)

dbPath = dbRootPath + "central.db"

hashmap = {}

with open("database.txt", "r") as f:
    for line in f:
        shortR, longR = line.split()
        hashmap[shortR] = longR

try:
    os.remove(dbPath)
except FileNotFoundError:
    pass
con = sqlite3.connect(dbPath)
cur = con.cursor()
con.execute('''create table if not exists urlMap (short varchar(50) primary key, long varchar(150) not null);''')
cur.executemany("INSERT OR IGNORE INTO urlMap(short, long) VALUES(?, ?)", hashmap.items())
con.commit()
con.close()