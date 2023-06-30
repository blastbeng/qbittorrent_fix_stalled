import os
import time
import qbittorrentapi
import datetime as dt

from scheduler import Scheduler
from dotenv import load_dotenv

load_dotenv()

HOST=os.environ.get("HOST"),
PORT=int(os.environ.get("PORT")),
USER=os.environ.get("USER"),
PASS=os.environ.get("PASS"),

schedule = Scheduler()

def fix_stalled():
    conn_info = dict(
        host=HOST,
        port=PORT,
        username=USER,
        password=PASS,
    )
    qbt_client = qbittorrentapi.Client(**conn_info)

    stalled = qbt_client.torrents.info(status_filter="stalled_downloading")

    for torrent in stalled.data:
        if torrent.info.num_seeds == 0 and torrent.info.time_active > 1800:
            qbt_client.torrents.bottom_priority(torrent_hashes=torrent.hash)
        

schedule.cyclic(dt.timedelta(minutes=30), fix_stalled)

while True:
    schedule.exec_jobs()
    time.sleep(1)
