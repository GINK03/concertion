import pandas as pd
from os import environ as E
from pathlib import Path
import numpy as np
import glob
import json
import datetime
from dataclasses import dataclass, asdict, astuple
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import psutil
import os
import sys
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup

try:
    PARENT_DIR = Path(__file__).resolve().parent.parent
    TOP_DIR = Path(__file__).resolve().parent.parent.parent
    sys.path.append(f"{PARENT_DIR}")
    import TwitterIFrames

    sys.path.append(f'{TOP_DIR}')
    from Web import GetDigest
except:
    raise Exception("cannot import other local libs.")

HOME = E['HOME']

HERE = Path(__file__).resolve().parent
FILE = Path(__file__).name
NAME = Path(__file__).name.replace(".py", "")


@dataclass
class TimeFreq:
    time: datetime.datetime
    freq: int


def _pre_process(json_fn):
    if Path(json_fn).is_dir():
        return None
    link_tfs = []
    for line in open(json_fn):
        try:
            # print(line.strip())
            line = line.strip()
            obj = json.loads(line)
            link, date, time = [obj[x] for x in ['link', 'date', 'time']]
            tf = TimeFreq(datetime.datetime.strptime(f'{date} {time}', "%Y-%m-%d %M:%H:%S"), 1)
            link_tfs.append((link, tf))
        except:
            continue
    return link_tfs


def pre_process(N=20000, DAYS=3):
    """
    1. 最初に普通に最新のfavからデータを処理する
    2. HOME/.mnt/favにあるデータから処理する
    3. mutable性（過去にあまり遡れない性質になる、は許容する）
    4. timeはマシンのunixtime時間の違いによりUTC, JSTが混在するので、JSTを優先するため、最小値を採用
    5. dateは3日前まで見る
    """
    link_tf = {}
    target_pool = sorted(glob.glob(f'{HOME}/.mnt/fav*'))[-1]
    json_fns = []
    for user_dir in glob.glob(f'{target_pool}/*')[-N:]:
        for json_fn in glob.glob(f'{user_dir}/*'):
            json_fns.append(json_fn)

    with ProcessPoolExecutor(max_workers=psutil.cpu_count()) as exe:
        for _link_tfs in tqdm(exe.map(_pre_process, json_fns), total=len(json_fns), desc=f"[{FILE}] data collect recent favs from fav01 ~ favNN."):
            if _link_tfs is None:
                continue
            for link, tf in _link_tfs:
                if link not in link_tf:
                    link_tf[link] = tf
                else:
                    link_tf[link].freq += tf.freq
                    link_tf[link].time = min(tf.time, link_tf[link].time)

    df = pd.DataFrame({'link': list(link_tf.keys()), 'date': [tf.time.strftime("%Y-%m-%d") for tf in link_tf.values()], 'datetime': [tf.time for tf in link_tf.values()], 'freq': [tf.freq for tf in link_tf.values()]})
    df.sort_values(by=['freq'], ascending=False, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= pd.to_datetime(datetime.datetime.now().strftime("%Y-%m-%d")) - datetime.timedelta(days=DAYS)]

    shrink: List[pd.DataTime] = []
    for date, sub in df.groupby(by=["date"]):
        sub = sub.sort_values(by=['freq'], ascending=False)[:1000]
        shrink.append(sub)
    shrink: pd.DataTime = pd.concat(shrink)
    shrink.to_csv(f'{HERE}/var/{NAME}_pre_process.csv', index=None)


def put_local_html():
    """
    ../TwitterIFrames/PutLocaHtml.pyを呼び出し、実行
    """
    df = pd.read_csv(f'{HERE}/var/{NAME}_pre_process.csv')
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    for url, date in zip(df.link, df.date):
        TwitterIFrames.PutLocaHtml.put_local_html(url=url, date=date)


def _refrect_html(arg):
    key, objs = arg
    for day, digest, url in tqdm(objs, desc=f"[{FILE}] refrect_html in mini processes..."):
        ret = TwitterIFrames.ReflectHtml.reflect_html(key=key, day=day, digest=digest)
        if ret is None:
            print(f'[{FILE}] not correct works, https://concertion.page/twitter/input/{day}/{digest}', file=sys.stderr)


def refrect_html():
    """
    1. ../TwitterIFrames/ReflectHtml.pyを呼び出す
    2. keyはダミーを採用
    3. digestは共通ライブラリから使用
    """
    NUM = psutil.cpu_count() * 2
    df = pd.read_csv(f'{HERE}/var/{NAME}_pre_process.csv')
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    key_list: Dict[int, List[Tuple[str, str, str]]] = {}
    for idx, (url, day) in enumerate(zip(df.link, df.date)):
        key = idx % NUM
        digest = GetDigest.get_digest(url)
        if not isinstance(day, str):
            raise Exception("day object must be str.", type(day))
        if len(day) > len("YYYY-mm-dd"):
            raise Exception("day value must be %Y-%m-%d.")
        if key not in key_list:
            key_list[key] = []
        key_list[key].append((day, digest, url))
    args = [(key, objs) for key, objs in key_list.items()]
    with ProcessPoolExecutor(max_workers=NUM) as exe:
        for ret in tqdm(exe.map(_refrect_html, args, timeout=60*30), total=len(args), desc=f"[{FILE}] refrect_html..."):
            ret


def post_process():
    df = pd.read_csv(f'{HERE}/var/{NAME}_pre_process.csv')
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    MAX_NUM = 800
    for day, sub in df.groupby(by=["date"]):
        tmp = ""
        for idx, (url, freq) in enumerate(zip(sub.link, sub.freq)):
            if idx > MAX_NUM:
                break
            digest = GetDigest.get_digest(url)
            if Path(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}').exists():
                try:
                    with open(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}') as fp:
                        html = fp.read()
                    if html == "":
                        Path(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}').unlink()
                        continue
                    soup = BeautifulSoup(html, 'lxml')
                    sandbox_root = soup.find(attrs={'class': 'SandboxRoot'})
                    sandbox_root.find(attrs={'class': 'EmbeddedTweet'})["style"] = "margin: 0 auto; margin-top: 30px;"
                    """
                    styleの最後のヘッダー外の要素を取り出して最後に追加する
                    """
                    outer_style = soup.find_all('style')[-1]
                    """
                    imgのURLをLocalURLに張替え
                    """
                    imagegrids = soup.find_all('a', {'class': 'ImageGrid-image'})
                    for imagegrid in imagegrids:
                        src = imagegrid.find('img').get('src')
                        imagegrid['href'] = src
                    images = soup.find_all('a', {'class': 'MediaCard-mediaAsset'})
                    for image in images:
                        src = image.find('img').get('src')
                        image['href'] = src
                except Exception as exc:
                    print(f'[{FILE}] post_process exception, exc = {exc}', file=sys.stderr)
                """
                styleの読み込みは一回だけでOK
                """
                if idx == MAX_NUM or idx == 0:
                    tmp += str(sandbox_root) + str(outer_style)
                else:
                    tmp += str(sandbox_root)
        head = f"<html><head><title>{day}</title></head><body>"
        tail = "</body>"
        with open(f'{HERE}/var/htmls/{day}.html', 'w') as fp:
            fp.write(head + tmp + tail)


def run():
    pre_process()
    put_local_html()
    refrect_html()
    post_process()


if __name__ == "__main__":
    # pre_process(N=20000, DAYS=30)
    # put_local_html()
    # refrect_html()
    post_process()
