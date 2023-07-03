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
        logging.info("--- START fix_stalled START ---")
        conn_info = dict(
            host=os.environ.get("HOST"),
            port=int(os.environ.get("PORT")),
            username=os.environ.get("USER"),
            password=os.environ.get("PASS"),
        )
        logging.info("Connecting...")
        qbt_client = qbittorrentapi.Client(**conn_info)

        decrease_prio(qbt_client, qbt_client.torrents.info(status_filter="stalled_downloading"))
        decrease_prio(qbt_client, qbt_client.torrents.info(status_filter="active"))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)
    finally:
        logging.info("--- END fix_stalled END ---")
          

def decrease_prio(qbt_client, data):
    for torrent in data:
        logging.info("Torrent: %s", torrent.info.hash)
        logging.info("      - hash:        %s", torrent.info.hash)
        logging.info("      - state:       %s", torrent.info.state)
        logging.info("      - num_seeds:   %s", torrent.info.num_seeds)
        logging.info("      - time_active: %s", str(torrent.info.time_active))
        if torrent.state == 'stalledDL' and torrent.info.time_active > 1800:
            logging.info("      - action: %s", "setting bottom priority")
            qbt_client.torrents.bottom_priority(torrent_hashes=torrent.hash)
        elif torrent.state == 'metaDL' and torrent.info.num_seeds == 0 and torrent.info.time_active > 1800:
            logging.info("      - action: %s", "setting bottom priority")
            qbt_client.torrents.bottom_priority(torrent_hashes=torrent.hash)
        elif torrent.state == 'downloading' and torrent.info.num_seeds == 0 and torrent.info.time_active > 1800:
            logging.info("      - action: %s", "setting bottom priority")
            qbt_client.torrents.bottom_priority(torrent_hashes=torrent.hash)
        else:
            logging.info("      - action: %s", "skipped")



fix_stalled()

schedule.cyclic(dt.timedelta(minutes=30), fix_stalled)

while True:
    schedule.exec_jobs()
    time.sleep(1)
