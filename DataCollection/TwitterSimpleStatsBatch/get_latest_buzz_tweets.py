import glob
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
import re
import gzip
import json
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

TOP = Path(__file__).resolve().parent.parent.parent

now = datetime.datetime.now()


def get_sf(url):
    sf_str = re.search("/(\d{1,})$", url).group(1)
    sf = datetime.datetime.fromtimestamp(((int(sf_str) >> 22) + 1288834974657) / 1000)
    sf_jst = sf + datetime.timedelta(seconds=60 * 60 * 9)
    return sf_jst


def proc(user_dir):
    username = Path(user_dir).name

    objs = []
    for feed in (Path(user_dir) / "FEEDS/").glob("*"):
        if re.search("FAVORITES_.*?.gz", feed.name) is None:
            continue
        ts = datetime.datetime.strptime(feed.name, "FAVORITES_%Y-%m-%d %H:%M:%S.gz")
        # if not (now - ts <= datetime.timedelta(days=1)):
        #    continue
        with gzip.open(feed, "rt") as fp:
            for line in fp:
                line = line.strip()
                obj = json.loads(line)
                status_url = obj["status_url"]
                sf_jst = get_sf(status_url)
                if not (now - sf_jst <= datetime.timedelta(days=1)):
                    continue
                obj = {"status_url": status_url, "sf_jst": sf_jst.strftime("%Y-%m-%d")}
                objs.append(obj)
    tmp = pd.DataFrame(objs)
    tmp.drop_duplicates(subset=["status_url"], keep="last", inplace=True)
    return tmp


user_dirs = glob.glob(Path("~/.mnt/nfs/favs10/*").expanduser().__str__())[:1000000]
objs = []
# for user_dir in tqdm(user_dirs):
with ProcessPoolExecutor(max_workers=16) as exe:
    for ret in tqdm(exe.map(proc, user_dirs), total=len(user_dirs)):
        objs.append(ret)

df = pd.concat(objs)
df["c"] = 1
df = df.groupby(by=["status_url", "sf_jst"])["c"].sum().reset_index()
df.sort_values(by=["sf_jst", "c"], ascending=False, inplace=True)
df.to_csv(TOP / "var/latest_buzz.csv", index=None)
