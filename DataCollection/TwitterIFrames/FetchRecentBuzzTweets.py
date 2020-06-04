import socket
import re
import gzip
from pathlib import Path
import glob
import datetime
from tqdm import tqdm
from collections import namedtuple
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import sys
from os import environ as E

HOME = E.get("HOME")
FILE = Path(__file__).name
NAME = FILE.replace(".py", "")
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__).resolve().parent.parent.parent

FnTs = namedtuple('FnTs', ['fn', 'ts'])
LinkTs = namedtuple('LinkTs', ['link', 'date', 'ts'])


def process(fnts):
    """
    1. ツイートのバズり具合をカウント
    2. threadがパフォーマンス効率が良かった　
    """
    global objs
    fn, ts = (fnts.fn, fnts.ts)
    try:
        for line in gzip.open(fn, "rt"):
            line = line.strip()
            obj = json.loads(line)
            status_url = obj['status_url']
            snowflake = int(re.search("/(\d{1,})$", status_url).group(1))
            # UTC!
            ts = datetime.datetime.fromtimestamp(((snowflake >> 22) + 1288834974657) / 1000)

            date = ts.strftime("%Y-%m-%d")
            ts = ts.strftime("%Y-%m-%d %M:%D:%S")
            linkts = LinkTs(link=status_url, date=date, ts=ts)
            if linkts not in objs:
                objs[linkts] = 0
            objs[linkts] += 1
    except Exception as exc:
        print(f'[{FILE}] exc = {exc}', file=sys.stderr)


objs = {}


def run():
    """
    1. 最新のツイートのバズった状態を見てくる
    2. link, date, tsのnamedtupleの数を数えている
    3. ディレクトリは一番新しいものを選択
    4. sort_values(by=['date', 'freq']) することで、dateが最新であることを担保
    """
    global objs
    files = []

    input_dir = sorted(glob.glob(f'{HOME}/.mnt/favs*'))[-1]
    if socket.gethostname() in {"Fubuki"}:
        print("Fubukiでテストします")
        user_files = glob.glob(f'{HOME}/sdc/*/FEEDS/FAVORITES_*')[-10000:]
    else:
        user_files = glob.glob(f'{input_dir}/*/FEEDS/FAVORITES_*')[-10000:]
    for fn in tqdm(user_files, desc=f"[{FILE}] 最新のバズったtweetを見ます, {Path(input_dir).name}"):
        ts = Path(fn).stat().st_mtime
        ts = datetime.datetime.fromtimestamp(ts)
        fnts = FnTs(fn=fn, ts=ts)
        files.append(fnts)
    files = sorted(files, key=lambda x: x.ts)
    with ThreadPoolExecutor(max_workers=16) as exe:
        for ret in tqdm(exe.map(process, files), total=len(files), desc=f"[{FILE}] ツイートのカウントとアグリゲーションをしています..."):
            ret
    df = pd.DataFrame(list(objs.keys()))
    df['freq'] = list(objs.values())
    df.sort_values(by=['date', 'freq'], ascending=False, inplace=True)
    df.to_csv(f'{TOP_DIR}/var/{NAME}.csv', index=None)
    objs = {}


if __name__ == '__main__':
    run()
