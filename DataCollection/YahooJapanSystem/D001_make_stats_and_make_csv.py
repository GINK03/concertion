import pandas as pd
import glob
from pathlib import Path
import pickle
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Union
from tqdm import tqdm
FILE = Path(__file__).name
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent
try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web.Structures import TitleUrlDigestScore
except Exception as exc:
    raise Exception(exc)

INPUT_FOLDER = f'{TOP_FOLDER}/var/YJ/frequency_watch/'

def process(fn1: str) -> Union[TitleUrlDigestScore, None]:
    """
    Args:
        - fn1: 読み込みファイル名
    Returns:
        - Union[TitleUrlDigestScore, None]: 失敗時はNoneが帰る
    """
    try:
        title_url_digest_score = pickle.load(open(fn1, 'rb'))
    except Exception as exc:
        print(f'[{FILE}] exc = {exc}.', file=sys.stderr)
        Path(fn1).unlink()
        return None
    return title_url_digest_score

def run():
    args = []
    for fn0 in glob.glob(f'{INPUT_FOLDER}/*'):
        for fn1 in glob.glob(f'{fn0}/*.pkl'):
            args.append(fn1)
    
    objs = []
    try:
        with ThreadPoolExecutor(max_workers=32) as exe:
            for r in exe.map(process, args, timeout=60*5):
                if r is None:
                    continue
                objs.append(r)
    except Exception as exc:
        print(f"[{FILE}] exc = {exc}", file=sys.stderr)
    
    # clean up pkls
    for fn0 in glob.glob(f'{INPUT_FOLDER}/*'):
        for fn1 in glob.glob(f'{fn0}/*.pkl'):
            Path(fn1).unlink()

    df = pd.DataFrame(objs)
    objs = []
    for (url, category), sub in df.groupby(by=['url', 'category']):
        obj = {'url': url, 'title':sub.iloc[0].title, 'category': category, 'score': sub.score.sum(), 'first_date': sub.date.min()}
        objs.append(obj)
    df = pd.DataFrame(objs)

    df['yyyy-mm-dd hh'] = df.first_date.apply(lambda x:x.strftime('%Y-%m-%d %H'))

    OUT_DIR = f'{TOP_FOLDER}/var/YJ/ranking_stats'
    Path(OUT_DIR).mkdir(exist_ok=True, parents=True)

    for day_hour, sub in df.groupby('yyyy-mm-dd hh'):
        sub = sub.copy()
        sub.sort_values(by=['score'], inplace=True, ascending=False)
        sub.to_csv(f'{OUT_DIR}/{day_hour}.csv', index=None)
    
    # デイリー粒度のランキング
    DAILY_OUT_DIR = f'{TOP_FOLDER}/var/YJ/ranking_stats_daily'
    Path(DAILY_OUT_DIR).mkdir(exist_ok=True, parents=True)
    df['yyyy-mm-dd'] = df.first_date.apply(lambda x:x.strftime('%Y-%m-%d'))
    for day, sub in df.groupby('yyyy-mm-dd'):
        sub = sub.copy()
        Path(f'{DAILY_OUT_DIR}/{day}').mkdir(exist_ok=True, parents=True)
        for day_hour, sub2 in sub.groupby('yyyy-mm-dd hh'):
            sub2 = sub2.copy()
            sub2.sort_values(by=['score'], inplace=True, ascending=False)
            sub2.to_csv(f'{DAILY_OUT_DIR}/{day}/{day_hour}.csv', index=None)

if __name__ == '__main__':
    run()
