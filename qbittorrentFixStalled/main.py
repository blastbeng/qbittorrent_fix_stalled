import os
import sys
import time
import logging
import qbittorrentapi
import datetime as dt

from scheduler import Scheduler
from dotenv import load_dotenv

load_dotenv()

schedule = Scheduler()

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get("LOG_LEVEL")),
        datefmt='%Y-%m-%d %H:%M:%S')

def fix_stalled():
    try:
        conn_info = dict(
            host=os.environ.get("HOST"),
            port=os.environ.get("PORT"),
            username=os.environ.get("USER"),
            password=os.environ.get("PASS"),
        )
        logging.info("Connecting...")
        qbt_client = qbittorrentapi.Client(**conn_info)

        logging.info("Getting stalled torrents")
        stalled = qbt_client.torrents.info(status_filter="stalled_downloading")

        for torrent in stalled.data:
            if torrent.info.num_seeds == 0 and torrent.info.time_active > 1800:
                qbt_client.torrents.bottom_priority(torrent_hashes=torrent.hash)
                logging.info("Setting bottom priority on %s", torrent.name)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
          
fix_stalled()

schedule.cyclic(dt.timedelta(minutes=30), fix_stalled)

while True:
    schedule.exec_jobs()
    time.sleep(1)
