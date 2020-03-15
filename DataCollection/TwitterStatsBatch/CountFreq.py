from concurrent.futures import ThreadPoolExecutor
import pickle
import pandas as pd
import glob
from collections import namedtuple
from pathlib import Path
from tqdm import tqdm
import json
from concurrent.futures import ProcessPoolExecutor
import datetime
import shutil
from os import environ as E

FILE = Path(__file__).name
NAME = FILE.replace(".py", "")
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__).resolve().parent.parent

Datum = namedtuple('Datum', ['link', 'date', 'time', 'tz', 'created_at'])


def proc(arg):
    key, sub_dirs = arg
    try:
        datum_freq = {}
        for sub_dir in tqdm(sub_dirs, desc="in a child process"):
            # print(key, sub_dir)
            username = Path(sub_dir).name
            if not Path(sub_dir).is_dir():
                continue
            for fn in glob.glob(f'{sub_dir}/*'):
                with open(fn) as fp:
                    for line in fp:
                        line = line.strip()
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        # print(json.dumps(obj, indent=2, ensure_ascii=False))
                        datum = Datum(obj['link'], obj['date'], obj['time'], obj['timezone'], obj['created_at'])
                        # print(username, datum)
                        if datum not in datum_freq:
                            datum_freq[datum] = 0
                        datum_freq[datum] += 1
        with open(f'{HERE}/var/{NAME}/{key:06d}.pkl', 'wb') as fp:
            pickle.dump(datum_freq, fp)
    except Exception as exc:
        print(exc)

def paralell_process(sub_dir):
    time_th = datetime.datetime.now() - datetime.timedelta(days=3)
    ts = datetime.datetime.fromtimestamp(Path(sub_dir).stat().st_mtime)

    if time_th > ts and E.get("TEST") != "1":
        return None
    # print(sub_dir, ts)
    return sub_dir


def run():
    sub_dirs = []
    for dir in glob.glob(f'{HERE}/mount/matching.jp/var/favorites*'):
        if not Path(dir).is_dir():
            continue

        if E.get("TEST") is None:
            arg_dirs = list(glob.glob(f'{dir}/*'))
        else:
            arg_dirs = list(glob.glob(f'{dir}/*'))[:100]

        with ThreadPoolExecutor(max_workers=100) as exe:
            for ret in tqdm(exe.map(paralell_process, arg_dirs), total=len(arg_dirs), desc=f"ScanSubDirs name = {Path(dir).name}"):
                # print(ret, E.get("TEST"), len(sub_dirs))
                if ret is None:
                    continue
                sub_dirs.append(ret)

    print('start to create args...')
    SPLIT = max(len(sub_dirs)//10000, 1)
    args = {}
    for idx, sub_dir in enumerate(sub_dirs):
        key = idx % SPLIT
        if key not in args:
            args[key] = []
        args[key].append(sub_dir)
    args = [(key, sub_dirs) for key, sub_dirs in args.items()]
    print('finish to create args...')
    # This is output dir
    out_dir = f'{HERE}/var/{NAME}'
    if Path(out_dir).exists():
        shutil.rmtree(out_dir)
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    # for arg in args:
    #    proc(arg)
    with ProcessPoolExecutor(max_workers=16) as exe:
        for ret in tqdm(exe.map(proc, args), total=len(args), desc="ParallelRun"):
            ret


if __name__ == "__main__":
    run()
