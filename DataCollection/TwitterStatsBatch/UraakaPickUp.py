import time
import schedule
import requests
import datetime
from dataclasses import dataclass, asdict, astuple
import glob
import json
import sys
from os import environ as E
import os
import MeCab
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import random
import re
from pathlib import Path
from collections import namedtuple
import click
import psutil
from bs4 import BeautifulSoup
from typing import Tuple, Union, Dict, List, Set
import shutil
import gzip

Tweet = namedtuple("Tweet", ["tweet", "username", "photos"])

HOME = E.get("HOME")
HERE = Path(__file__).resolve().parent
FILE = Path(__file__).name
NAME = Path(__file__).name.replace(".py", "")
PARENT_DIR = Path(__file__).resolve().parent.parent
TOP_DIR = Path(__file__).resolve().parent.parent.parent

try:
    sys.path.append(f"{PARENT_DIR}")
    import TwitterIFrames

    sys.path.append(f"{TOP_DIR}")
    from Web import GetDigest
except:
    raise Exception("cannot import other local libs.")

mecab = MeCab.Tagger("-O wakati -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd")
assert mecab.parse("新型コロナウイルス").strip().split() == ["新型コロナウイルス"], "辞書が最新ではありません"


def _statical_pick_up(arg):
    keyword, user_dir = arg
    term_freq = {}
    term_freq2 = {}
    cnt = 0
    cnt2 = 0
    for json_fn in glob.glob(f"{user_dir}/*"):
        try:
            tweets = []
            
            if re.search("\.gz$", json_fn):
                fp = gzip.open(json_fn, "rt")
            else:
                fp = open(json_fn)
            
            with fp:
                for line in fp:
                    line = line.strip()
                    try:
                        obj = json.loads(line)
                    except:
                        continue
                    tweets.append(Tweet(obj["tweet"], f"@{obj['username']}", obj["photos"]))
        except:
            continue

        require_size = 1
        # idxs = [idx for idx, tweet in enumerate(tweets) if keyword in set(mecab.parse(tweet.tweet.lower()).split())]
        idxs = [idx for idx, tweet in enumerate(tweets) if keyword in tweet.tweet.lower()]

        for idx in idxs:
            batch = tweets[min(idx - 3, 0): idx + 3]
            cnt += 1

            for term in set(mecab.parse(" ".join([b.tweet for b in batch]).lower()).strip().split()):
                if term not in term_freq:
                    term_freq[term] = 0
                term_freq[term] += 1

            for photos in [b.photos for b in batch]:
                for photo in photos:
                    if photo is None:
                        continue
                    if photo not in term_freq:
                        term_freq[photo] = 0
                    term_freq[photo] += 1

            for username in [b.username for b in batch]:
                if username not in term_freq:
                    term_freq[username] = 0
                term_freq[username] += 1

        if len(tweets) != 0:
            for N in range(5):
                idx2 = random.choice(list(range(len(tweets))))
                batch2 = tweets[min(idx2 - 3, 0): idx2 + 3]
                cnt2 += 1
                try:
                    for term in set(mecab.parse(" ".join([b.tweet for b in batch2]).lower()).strip().split()):
                        if term not in term_freq2:
                            term_freq2[term] = 0
                        term_freq2[term] += 1
                except Exception as exc:
                    """ 形態素解析に失敗することがある？ """
                    print(exc)
                for photos in [b.photos for b in batch2]:
                    for photo in photos:
                        if photo is None:
                            continue
                        if photo not in term_freq2:
                            term_freq2[photo] = 0
                        term_freq2[photo] += 1

                for username in [b.username for b in batch2]:
                    if username not in term_freq2:
                        term_freq2[username] = 0
                    term_freq2[username] += 1
    return term_freq, cnt, term_freq2, cnt2


def statical_pickup(count=20000, keyword="裏垢"):
    """
    1. 統計的な手法によりkeywordを使用するアカウントをそれ以外の分布から比較して大きいアカウント、単語、写真を取り出す
    2. 後処理が必要
    """
    print(f"[{FILE}] keyword={keyword}, sampling_size={count}で処理を開始します")

    Path(f"{HERE}/var/{NAME}/results").mkdir(exist_ok=True, parents=True)
    term_freq, term_freq2 = {}, {}
    cnt, cnt2 = 0, 0

    most_recent_disk = sorted(glob.glob(f"{HOME}/.mnt/favs*"))[-1]
    print(f"[{FILE}] target disk is {most_recent_disk}")
    args = [(keyword, user_dir) for user_dir in glob.glob(f"{most_recent_disk}/*")[-count:]]
    """ this is adhoc """
    with ProcessPoolExecutor(max_workers=psutil.cpu_count()) as exe:
        for _term_freq, _cnt, _term_freq2, _cnt2 in tqdm(exe.map(_statical_pick_up, args), total=len(args), desc=f"[{FILE}] statical_pickup..."):
            cnt += _cnt
            for term, freq in _term_freq.items():
                if term not in term_freq:
                    term_freq[term] = 0
                term_freq[term] += freq

            cnt2 += _cnt2
            for term, freq in _term_freq2.items():
                if term not in term_freq2:
                    term_freq2[term] = 0
                term_freq2[term] += freq

    # サンプルサイズが減りすぎてしまうので、ターゲットに観測されたtermはベースラインで1とする
    delta_terms = set(term_freq) - set(term_freq2)
    for delta_term in delta_terms:
        term_freq[delta_term] = 1
    terms = list(set(term_freq.keys()) & set(term_freq2.keys()))
    terms = [term for term in terms if re.search("^[a-z]{1,}$", term) is None and re.search("^[0-9]{1,}", term) is None]

    df = pd.DataFrame({"term": terms, "term_num": [term_freq[term] for term in terms], "term_num2": [term_freq2[term] for term in terms]})
    # サンプルサイズの正規化
    # fix = lambda x: int(x * (cnt/cnt2))
    df["prob"] = df["term_num"] / cnt
    df["prob2"] = df["term_num2"] / cnt2
    df["total"] = df["term_num"] + df["term_num2"]
    df["rel"] = df["prob"] / (df["prob"] + df["prob2"])
    df.sort_values(by=["rel"], ascending=False, inplace=True)
    df.to_csv(f"{HERE}/var/{NAME}/results/{keyword}_{count}.csv", index=None)


def filter_statical_pickup():
    """
    1. 統計的手法はノイズがそれなりに入るため、ヒューリスティクスで落とす
    """
    files = glob.glob(f"{HERE}/var/{NAME}/results/*.csv")
    Path(f"{HERE}/var/{NAME}/filter").mkdir(exist_ok=True, parents=True)

    for file in files:
        name = Path(file).name
        df = pd.read_csv(file)
        # user
        df1 = df[df["term"].apply(lambda x: "@" in str(x))]
        t1 = sorted(df1[df1.rel >= 0.5].total.tolist())
        th = t1[int(len(t1) * 9 / 10)]
        df1 = df1[df1["total"] >= th]
        df1.to_csv(f"{HERE}/var/{NAME}/filter/users_{name}", index=None)

        # term
        df2 = df[df["term"].apply(lambda x: "@" not in str(x) and ".jpg" not in str(x))]
        t2 = sorted(df2[df2.rel >= 0.5].total.tolist())
        th = t2[int(len(t2) * 9 / 10)]
        df2 = df2[df2["total"] >= th]
        df2.to_csv(f"{HERE}/var/{NAME}/filter/terms_{name}", index=None)

        # pics
        df3 = df[df["term"].apply(lambda x: ".jpg" in str(x))]
        t3 = sorted(df3[df3.rel >= 0.5].total.tolist())
        th = t3[int(len(t3) * 3 / 10)]
        df3 = df3[df3["total"] >= 10]
        df3 = df3[df3["total"] >= th]
        df3 = df3[df["rel"] >= 0.90]

        df3.to_csv(f"{HERE}/var/{NAME}/filter/pics_{name}", index=None)


@dataclass
class DateLikePhotos:
    date: str
    likes_count: int
    photos: List[str]
    link: str


def _find_joinable_tweet_ids(arg) -> List[Tuple[str, List[str]]]:
    user_dir = arg
    rets = []
    for json_fn in glob.glob(f"{user_dir}/*"):
        try:
            # tweets = []
            if re.search("\.gz$", json_fn):
                fp = gzip.open(json_fn, "rt")
            else:
                fp = open(json_fn)

            with fp:
                for line in fp:
                    line = line.strip()
                    try:
                        obj = json.loads(line)
                    except:
                        continue
                    dlp = DateLikePhotos(obj["date"], obj["likes_count"], obj["photos"], obj["link"])
                    ret = (obj["link"], dlp)
                    rets.append(ret)
                # tweets.append(Tweet(obj['tweet'], f"@{obj['username']}", obj["photos"]))
        except:
            continue
    return rets


def find_joinable_tweet_ids(count=20000):
    """
    1. pic_hogehoge.csvは強調されたimage urlであるが、もとのtweet idを失っている
    2. 再びfavのjsonをスキャンしてtweet id, image url, scoreをジョインする
    3. df.rel >= x, のxはハイパーパラメータ
    OUTPUT: pd.DataFrame, link,photosのcsv
    """
    for pic_csv_file in glob.glob(f"{HERE}/var/{NAME}/filter/pics_*.csv"):
        keyword_name = re.search(r'pics_(.{1,}).csv', pic_csv_file).group(1)

        photos: Set[str] = set()

        df = pd.read_csv(pic_csv_file)
        # df = df[df.rel >= 0.93]
        photos |= set(df.term.tolist())
        """ fav00 ~  favXXまでナンバリングされている """
        most_recent_disk = sorted(glob.glob(f"{HOME}/.mnt/favs*"))[-1]
        args = [(user_dir) for user_dir in tqdm(glob.glob(f"{most_recent_disk}/*")[-count:], desc=f"[{FILE}] scan files in find_joinable_tweet_ids...")]

        link_dlp = {}
        with ProcessPoolExecutor(max_workers=psutil.cpu_count()) as exe:
            for _rets in tqdm(exe.map(_find_joinable_tweet_ids, args), total=len(args), desc=f"[{FILE}][{keyword_name}] joining photo url <-> tweet id..."):
                for link, dlp in _rets:
                    """
                    1. 特定のキーワードかそれ以外で動作を分ける
                    NOTE: "コロナ"のとき、画像以外も対象で、likes_count >= 100とする
                    """
                    if "コロナ" in keyword_name:
                        if dlp.likes_count >= 100:
                            link_dlp[link] = dlp
                    else:
                        if len(photos & set(dlp.photos)) != 0:
                            if link not in link_dlp:
                                link_dlp[link] = dlp

        df = pd.DataFrame({"link": list(link_dlp.keys()), "photos": [dlp.photos for dlp in link_dlp.values()], "likes_count": [dlp.likes_count for dlp in link_dlp.values()], "date": [dlp.date for dlp in link_dlp.values()]})
        df["photos"] = df["photos"].apply(json.dumps)
        df.to_csv(f"{HERE}/var/{NAME}/link_photos_date_likes_{keyword_name}.csv", index=None)


def put_local_html(N=10000):
    """
    1. ../TwitterIFrames/PutLocaHtml.pyを呼び出し、実行
    2. date, likes_countの順で高順にソートして、top Nを取り出す
    """
    for csv_file in glob.glob(f"{HERE}/var/{NAME}/link_photos_date_likes_*.csv"):
        df = pd.read_csv(csv_file)
        df.sort_values(by=["date", "likes_count"], ascending=False, inplace=True)
        df = df[:N]
        df["date"]: pd.Series[str] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        for url, date in zip(df.link, df.date):
            TwitterIFrames.PutLocaHtml.put_local_html(url=url, date=date)


def _refrect_html(arg):
    key, objs = arg
    for day, digest, url in tqdm(objs, desc=f"[{FILE}] refrect_html in mini processes..."):
        ret = TwitterIFrames.ReflectHtml.reflect_html(key=key, day=day, digest=digest)
        if ret is None:
            print(f"[{FILE}] not correct works, https://concertion.page/twitter/input/{day}/{digest}", file=sys.stderr)


def refrect_html(N=10000):
    """
    1. ../TwitterIFrames/ReflectHtml.pyを呼び出す
    2. keyはダミーを採用
    3. digestは共通ライブラリから使用
    4. NUM(プロセス数)はコア数の3倍を想定
    """
    NUM = psutil.cpu_count() * 3
    for csv_file in glob.glob(f"{HERE}/var/{NAME}/link_photos_date_likes_*.csv"):
        keyword_name = re.search(r"link_photos_date_likes_(.{1,}).csv", csv_file).group(1)
        df = pd.read_csv(csv_file)
        df.sort_values(by=["date", "likes_count"], ascending=False, inplace=True)
        df = df[:N]

        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        key_list: Dict[int, List[Tuple[str, str, str]]] = {}
        """
        一様にシャッフルしないと一部のProcessに負荷が偏りすぎる（おそらくhtml取得の失敗が再現されてしまうため）
        """
        urldays = [(url, day) for url, day in zip(df.link, df.date)]
        random.shuffle(urldays)
        for idx, (url, day) in enumerate(urldays):
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
        try:
            with ProcessPoolExecutor(max_workers=NUM) as exe:
                for ret in tqdm(exe.map(_refrect_html, args, timeout=60 * 30), total=len(args), desc=f"[{FILE}][{keyword_name}]refrect_html..."):
                    ret
        except Exception as exc:
            print(f'[{FILE}][{keyword_name}] error occured in parallel refrect_html, exc = {exc}', file=sys.stderr)


def _get_imgs(arg):
    """
    1. requestsで画像をgetするタイミングでハングアップすることがあるのでtimeoutを設ける
    """
    link, photos = arg
    original_image_digests = []
    original_image_urls = []

    out_dir = f'{TOP_DIR}/var/Twitter/original_images'
    link_digest = GetDigest.get_digest(link)
    map_out_file = f'{out_dir}/maps/{link_digest}'
    if Path(map_out_file).exists():
        return

    for photo in photos:
        digest = GetDigest.get_digest(photo)
        original_image_digests.append(digest)
        original_image_urls.append(photo)
        if Path(f'{TOP_DIR}/mnt/twitter_jpgs/{digest}').exists():
            continue
        try:
            with requests.get(photo, timeout=60) as r:
                binary = r.content
            with open(f'{TOP_DIR}/mnt/twitter_jpgs/{digest}', 'wb') as fp:
                fp.write(binary)
        except Exception as exc:
            tb_lineno = sys.exc_info()[2].tb_lineno
            print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)
    with open(f'{map_out_file}', 'w') as fp:
        fp.write(json.dumps({"link": link, "original_image_digests": original_image_digests, "original_image_urls": original_image_urls}, indent=2))


def get_imgs(N=10000):
    """
    1. var/Twitter/original_imagesに大きいimageを保存
    2. しきい値以上のimageが全部対象
    3. var/Twitter/original_images/binsにbinaries
    4. var/Twitter/original_images/mapsにマップ情報
    """
    for csv_file in glob.glob(f"{HERE}/var/{NAME}/link_photos_date_likes_*.csv"):
        keyword_name = re.search(r"link_photos_date_likes_(.{1,}).csv", csv_file).group(1)
        df = pd.read_csv(csv_file)
        df.sort_values(by=["date", "likes_count"], ascending=False, inplace=True)
        df = df[:N]

        args = [(link, photos) for link, photos in zip(df.link, df.photos.apply(json.loads))]
        with ProcessPoolExecutor(max_workers=24) as exe:
            for r in tqdm(exe.map(_get_imgs, args), desc=f"[{FILE}][{keyword_name}] get_imgs...", total=len(args)):
                r


def post_process(N=10000):
    """
    1. 静的なhtmlを日付粒度で作る
    2. 最新の情報を見ていないので別プロセスで構築する必要がある
    """
    for csv_file in glob.glob(f"{HERE}/var/{NAME}/link_photos_date_likes_*.csv"):
        keyword_name = re.search(r"link_photos_date_likes_(.{1,}).csv", csv_file).group(1)
        df = pd.read_csv(csv_file)
        df.sort_values(by=["date", "likes_count"], ascending=False, inplace=True)
        df = df[:N]

        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        Path(f'{HERE}/var/{NAME}/{keyword_name}/htmls').mkdir(exist_ok=True, parents=True)

        for day, sub in df.groupby(by=["date"]):
            sub = sub.copy()
            sub.sort_values(by=['likes_count'], ascending=False, inplace=True)
            args = []
            for idx, (url) in enumerate(sub.link):
                args.append((idx, day, url, len(df)))

            tmp = ""
            with ProcessPoolExecutor(max_workers=24) as exe:
                for _tmp in exe.map(_post_process_recent, args):
                    if _tmp is not None:
                        tmp += _tmp
            head = f"<html><head><title>{day}</title></head><body>"
            head = f"""<html><head><title>{keyword_name} {day}</title>
                <link rel="stylesheet" href="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css" />
                <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
                <script src="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
                <link href="//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight.min.css" type="text/css" rel="stylesheet" />
                <script src="//code.jquery.com/jquery-latest.js"></script>
                <script src="//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight.min.js" type="text/javascript" charset="utf-8"></script>
                </head><body>"""
            #            meta = """<section
            #          data-featherlight-gallery
            #          data-featherlight-filter="a">"""
            #            head += meta
            tail = "</section></body>"
            if not Path(f"{HERE}/var/{NAME}/{keyword_name}/htmls/{day}.html").exists():
                with open(f'{HERE}/var/{NAME}/{keyword_name}/htmls/{day}.html', 'w') as fp:
                    fp.write(head + tmp + tail)
            else:
                """
                1. もしデータのサイズが今回サンプルしたほうが大きければ上書き
                2. なぜなら、直近の50000件にサンプルが限定される
                """
                if len(head + tmp + tail) >= len(open(f'{HERE}/var/{NAME}/{keyword_name}/htmls/{day}.html').read()):
                    with open(f'{HERE}/var/{NAME}/{keyword_name}/htmls/{day}.html', 'w') as fp:
                        fp.write(head + tmp + tail)


def _post_process_recent(arg):
    """
    1. HTMLをローカルのファイルから作成する
    """

    idx, day, url, df_size = arg
    try:
        tmp = ""

        digest = GetDigest.get_digest(url)
        """
        originalのイメージとと都合するため, `var/Twitter/original_images/map` を参照
        """
        if not Path(f'{TOP_DIR}/var/Twitter/original_images/maps/{digest}').exists():
            print("イメージをフェッチできていないよ")
            return None
        original_image_digests = json.load(open(f'{TOP_DIR}/var/Twitter/original_images/maps/{digest}'))["original_image_digests"]
        if Path(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}').exists():
            try:
                with open(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}') as fp:
                    html = fp.read()
                if html == "":
                    Path(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}').unlink()
                    return None

                soup = BeautifulSoup(html, 'lxml')
                sandbox_root = soup.find(attrs={'class': 'SandboxRoot'})
                """
                EmbeddedTweetのコンテンツがない場合、取得できていないことになる
                """
                if sandbox_root.find(attrs={'class': 'EmbeddedTweet'}) is None:
                    raise Exception("There is no Tweet contents.")
                """
                EmbeddedTweetのタグにメタ情報である、"date"と"digest"を追加する
                """
                sandbox_root.find(attrs={'class': 'EmbeddedTweet'})["date"] = day
                sandbox_root.find(attrs={'class': 'EmbeddedTweet'})["day"] = day
                sandbox_root.find(attrs={'class': 'EmbeddedTweet'})["digest"] = digest
                """
                linkに評論のリンクを追加する　
                """
                append_soup = BeautifulSoup(sandbox_root.find(attrs={"class":"CallToAction"}).__str__(), "lxml")
                try:
                    if append_soup.find(attrs={"class":"CallToAction-text"}).string is not None:
                        append_soup.find(attrs={"class":"CallToAction-text"}).string = "評論する"
                        for a in append_soup.find_all("a", {"href": True}):
                            a["href"] = f"/TweetHyoron/{day}/{digest}"
                        sandbox_root.find(attrs={"class":"EmbeddedTweet-tweetContainer"}).insert(-1, append_soup)
                except Exception as exc:
                    print(exc)
                """
                tweetをセンタリング
                """
                sandbox_root.find(attrs={'class': 'EmbeddedTweet'})["style"] = "margin: 0 auto; margin-top: 30px;"
                """
                styleの最後のヘッダー外の要素を取り出して最後に追加する
                """
                outer_style = soup.find_all('style')[-1] if len(soup.find_all('style')) > 0 else ""

                """
                1. hueristics
                """
                if soup.find(attrs={'class': 'Tweet-card'}):
                    xa = soup.find(attrs={'class': 'Tweet-card'}).find_all('a')  # , {'class': 'MediaCard-mediaAsset'})
                    for a in xa:
                        a["target"] = "_blank"
                        if len(original_image_digests) > 0:
                            a['href'] = f'/twitter/jpgs/{original_image_digests[0]}'
                            # a["href"] = "#"
                            a["data-featherlight"] = 'image'
                """
                2. imgのURLをLocalURLに張替え
                """
                if soup.find('a', {'class': 'ImageGrid-image'}):
                    imagegrids = soup.find_all('a', {'class': 'ImageGrid-image'})
                    for imagegrid, original_image_digest in zip(imagegrids, original_image_digests):
                        src = imagegrid.find('img').get('src')
                        # imagegrid['href'] = src
                        imagegrid['href'] = f'/twitter/jpgs/{original_image_digest}'
                        # imagegrid['href'] = '#'
                        imagegrid["data-featherlight"] = 'image'
            except Exception as exc:
                lineno = sys.exc_info()[2].tb_lineno
                print(f'[{FILE}] post_process exception, exc = {exc}, url = {url}, line = {lineno}', file=sys.stderr)
                """
                1. NoneType object is not support assignmentが出ることがあり、htmlが不完全だと思われる
                2. 不完全なhtmlは持っていても仕方がない + 再取得したほうがいいのでunlinkする
                """
                # print(html)
                Path(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}').unlink()
            """
            styleの読み込みは一回だけでOK
            NOTE 10の倍数のとき読み込む
            """
            if idx == df_size - 1 or idx == 0 or idx % 10 == 0:
                tmp += str(sandbox_root) + str(outer_style)
            else:
                tmp += str(sandbox_root)
        return tmp
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)
        return None


def post_process_recent():
    """
    1. 静的なhtmlを日付粒度で作る
    2. 最新の情報だけに限定した特別版
    3. 重いので40ページごとsplit
    """
    Path(f'{HERE}/var/{NAME}/recents/').mkdir(exist_ok=True, parents=True)
    for csv_file in glob.glob(f"{HERE}/var/{NAME}/link_photos_date_likes_*.csv"):
        keyword_name = re.search(r"link_photos_date_likes_(.{1,}).csv", csv_file).group(1)
        df = pd.read_csv(csv_file)
        df.sort_values(by=["date", "likes_count"], ascending=False, inplace=True)
        df = df[:1000]

        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        args = []
        for idx, (day, url) in tqdm(enumerate(zip(df.date, df.link)), desc=f"[{FILE}] building html...", total=len(df)):
            args.append((idx, day, url, len(df)))

        tmps = []
        with ProcessPoolExecutor(max_workers=24) as exe:
            for _tmp in exe.map(_post_process_recent, args):
                if _tmp is not None:
                    tmps.append(_tmp)
        head = f"""<html><head><title>最新 {keyword_name}</title>
            <link rel="stylesheet" href="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css" />
            <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
            <script src="http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
            <link href="//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight.min.css" type="text/css" rel="stylesheet" />
            <script src="//code.jquery.com/jquery-latest.js"></script>
            <script src="//cdn.jsdelivr.net/npm/featherlight@1.7.14/release/featherlight.min.js" type="text/javascript" charset="utf-8"></script>
            </head><body>"""
        meta = """<section
      data-featherlight-gallery
      data-featherlight-filter="a">"""
        head += meta
        tail = "</section></body>"
        for i in range(100):
            start = i * 40
            end = i * 40 + 40
            """ adhocにキーワードを取り出し、めっちゃ不安 """
            """ スマホで見た時、次へ、が見えづらかったので linksに <br>を追加 """
            """ モーダルが使いにくい(削除するかも) """
            keyword = keyword_name.split("_")[0]
            links = f"""<br/><br/> <p align="center"><a href="/recent_stats/{keyword}/{i+1}">次のページ</a></p> <br/>"""
            saves = tmps[start:end]
            with open(f'{HERE}/var/{NAME}/recents/recent_{keyword_name}_{i}.html', 'w') as fp:
                fp.write(head + links + "".join(saves) + links + tail)


def delete_chrome_tmp():
    """
    1. chromeのtemp folderを消す
    2. inodeを食い尽くしてしまう
    """
    for tmp_dir in glob.glob(f'/tmp/ReflectHtml*'):
        if Path(tmp_dir).is_dir():
            try:
                shutil.rmtree(tmp_dir)
            except Exception as exc:
                tb_lineno = sys.exc_info()[2].tb_lineno
                print(f"[{FILE}] exc = exc, tb_lineno = {tb_lineno}", file=sys.stderr)


def run():
    """
    1. chromedriverが終了しないので強制終了する
    """
    os.system("pgrep chrome | xargs kill -9")
    statical_pickup(count=50000, keyword="裏垢女子")
    statical_pickup(count=50000, keyword="グラドル")
    statical_pickup(count=50000, keyword="同人")
    statical_pickup(count=50000, keyword="可愛い")
    filter_statical_pickup()
    find_joinable_tweet_ids(count=50000)
    put_local_html()
    refrect_html()
    get_imgs()
    post_process_recent()
    post_process()
    delete_chrome_tmp()
    print("finish run...")


if __name__ == "__main__":
    """
    1. このプログラムを単体で実行すると、4時間ごとにデータを収集して更新する
    """
    # while True:
    run()
    schedule.every(4).hours.do(run)
    while True:
        schedule.run_pending()
        time.sleep(1)
