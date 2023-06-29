import os
import time
import qbittorrentapi
import datetime as dt

from scheduler import Scheduler
from dotenv import load_dotenv

load_dotenv()

schedule = Scheduler()

def fix_stalled():
    conn_info = dict(
        host=os.environ.get("HOST"),
        port=int(os.environ.get("PORT")),
        username=os.environ.get("USER"),
        password=os.environ.get("PASS"),
    )
    qbt_client = qbittorrentapi.Client(**conn_info)

    stalled = qbt_client.torrents.info(status_filter="stalled_downloading")

    hashdropqueue = []

    for torrent in stalled.data:
        if torrent.info.num_seeds == 0 and torrent.info.time_active > 3600:
            hashdropqueue.append(torrent.hash)

    if len(hashdropqueue) > 0:
        qbt_client.torrents.decrease_priority(torrent_hashes=hashdropqueue)

schedule.cyclic(dt.timedelta(minutes=90), fix_stalled)

while True:
    schedule.exec_jobs()
    time.sleep(1)