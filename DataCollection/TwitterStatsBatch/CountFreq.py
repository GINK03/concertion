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
        for sub_dir in tqdm(sub_dirs, desc="in a child process", disable=True):
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
        # print('finished', key)
    except Exception as exc:
        print(exc)

def paralell_process(sub_dir):
    time_th = datetime.datetime.now() - datetime.timedelta(days=3)
    ts = datetime.datetime.fromtimestamp(Path(sub_dir).stat().st_mtime)
    # print(Path(sub_dir).name, ts, ts > time_th)
    if not (ts > time_th):
        return None
    return sub_dir


def run():
    sub_dirs = []
    """
    1. すべてのUtils/favorites.pyで保存したreplicaが対象
    """
    for dir in glob.glob(f'{HERE}/var/fav*'):
        if not Path(dir).is_dir():
            continue
        """
        1. 直近3日前までのデータに限定して対象のディレクトリをsub_dirsに追加
        2. btrfsの場合、古いディレクトリほどglob.globでスキャンしたときに前方に来るので、それを利用して末尾のN件を処理対象とする
        """
        arg_dirs = list(glob.glob(f'{dir}/*'))[-10000:]
        print('debug', len(arg_dirs))
        with ThreadPoolExecutor(max_workers=100) as exe:
            for ret in tqdm(exe.map(paralell_process, arg_dirs), total=len(arg_dirs), desc=f"ScanSubDirs name = {Path(dir).name}"):
                if ret is None:
                    continue
                sub_dirs.append(ret)
        print('debug', len(sub_dirs))

    print('start to create args...')
    SPLIT = max(len(sub_dirs)//100, 1)
    args = {}
    for idx, sub_dir in enumerate(sub_dirs):
        key = idx % SPLIT
        if key not in args:
            args[key] = []
        args[key].append(sub_dir)
    args = [(key, sub_dirs) for key, sub_dirs in args.items()]
    print('finish to create args...')
    # This is output dir
    """
    1. なんのツイートが何回favされたかを観測
    2. chunkでaggregateして次のプロセスでうまく処理する
    """
    out_dir = f'{HERE}/var/{NAME}'
    if Path(out_dir).exists():
        shutil.rmtree(out_dir)
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    # [proc(arg) for arg in args]
    with ProcessPoolExecutor(max_workers=16) as exe:
        for ret in tqdm(exe.map(proc, args), total=len(args), desc="ParallelRun"):
            ret

if __name__ == "__main__":
    run()
