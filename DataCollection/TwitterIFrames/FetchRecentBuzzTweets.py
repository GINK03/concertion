
from pathlib import Path
import glob
import datetime
from tqdm import tqdm
from collections import namedtuple
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import sys
FILE = Path(__file__).name
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__).resolve().parent.parent.parent

FnTs = namedtuple('FnTs', ['fn', 'ts'])
LinkTs = namedtuple('LinkTs', ['link', 'date', 'ts'])

# for fnts in tqdm(files):
def process(fnts):
    global objs
    fn, ts = (fnts.fn, fnts.ts)
    try:
        file_num = len(list(Path(fn).rglob('*')))
        if file_num == 0:
            return 
        for target in Path(fn).rglob('*'):
            for line in open(target):
                line = line.strip()
                obj = json.loads(line)
                link = obj['link']
                date = obj['date']
                ts = f"{obj['date']} {obj['time']}"
                linkts = LinkTs(link=link, date=date, ts=ts)
                if linkts not in objs:
                    objs[linkts] = 0
                objs[linkts] += 1
    except Exception as exc:
        print(f'[{__file__}] {exc}', file=sys.stderr)
objs = {}

def run():
    global objs
    files = []
    for fn in tqdm(glob.glob(f'{HERE}/var/favs/*')[-30000:]):
        ts = Path(fn).stat().st_mtime
        ts = datetime.datetime.fromtimestamp(ts)
        fnts = FnTs(fn=fn, ts=ts)
        print(fnts)
        files.append(fnts)
    files = sorted(files, key=lambda x:x.ts)
    # top 10000件のデータを取得する
    files = files[-30000:]
    with ThreadPoolExecutor(max_workers=16) as exe:
        for ret in tqdm(exe.map(process, files), total=len(files)):
            ret
    df = pd.DataFrame(list(objs.keys()))
    df['freq'] = list(objs.values())
    df.sort_values(by=['date', 'freq'], ascending=False, inplace=True)
    df.to_csv(f'{TOP_DIR}/var/{FILE.replace(".py", "")}.csv', index=None)
    objs = {}

if __name__ == '__main__':
    run()
