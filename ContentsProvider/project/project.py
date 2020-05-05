import gzip
import pickle
from flask import Flask, request, jsonify, render_template, make_response, abort
import json
import requests
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import pandas as pd
from bs4 import BeautifulSoup
from collections import namedtuple
import sys
import glob
import os
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter

FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent.parent
application = Flask(__name__)

try:
    sys.path.append(f'{TOP_DIR}')
    from Web import Base64EncodeDecode
    from Web import GenerateTop
    from Web import GenerateDailyYJRankingList
    from Web import AdhocYJHtmlReplace
    from Web.Structures import DayAndPath
    from Web import Hostname

    from Web import GetDay
    from Web import GenerateDailyYJAbstracts
    from Web import Login
    from Web import recent_stats
    from Web import TweetHyoron
    from Web import ResponsibleDevices
    application.register_blueprint(TweetHyoron.tweet_hyoron)
    # from Web import recent_guradoru
    # from Web import recent_corona
    # from Web import recent_kawaii
except Exception as exc:
    raise Exception(f"[{FILE}] import error exc = {exc}")

try:
    """ TwitterAPIのインポート """
    TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
    TWITTER_API_SECRET = os.environ['TWITTER_API_SECRET']
    TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
    TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
except Exception as exc:
    raise Exception(f"[{FILE}] there are missing of environ parameters of twitter apps, exc = {exc}")

try:
    """ flask_danceでTwitter OAuth機能を有効化"""
    application.secret_key = "supersekrit"
    blueprint = make_twitter_blueprint(api_key=TWITTER_API_KEY, api_secret=TWITTER_API_SECRET, redirect_url='/', redirect_to='/')
    application.register_blueprint(blueprint, url_prefix='/login')
    application.config["UPLOAD_FOLDER"] = 'uploads'
except Exception as exc:
    raise Exception(f"[{FILE}] there are something wrong with flask_dance, exc = {exc}")
print(f'[{FILE}] current hostname = {Hostname.hostname()}', file=sys.stdout)


@application.route("/")
def home() -> str:
    """
    トップ画面, GenerateTopにtwitterの認証情報を入力
    Args:
        - nothing
    Returns:
        - str: HTMLを返す
    """
    return GenerateTop.generate_top(twitter)


@application.route("/login")
def login():
    return Login.login()


@application.route('/daily_yj_abstracts/<name>')
def daily_yj_abstracts(name):
    return GenerateDailyYJAbstracts.generate_daily_yj_abstracts(name)


@application.route('/recent_stats/<category>/<page_num>')
def recent_stats_(category: str, page_num: str) -> str:
    return recent_stats.recent_stats(category, page_num)




@application.route("/backlog_of_stats/<category>", methods=['get'])
def backlog_of_stats_(category: str) -> str:
    head = f'<html><head><title>backlog of {category}</title></head><body>'
    body = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/{category}_50000/htmls/*'))):
        name = Path(fn).name
        date = name.replace(".html", "")
        tmp = f'''<a href="/backlog_of_stats/{category}/{name}">{date}</a><br>'''
        body += tmp
    tail = '</body></html>'
    html = head + body + ResponsibleDevices.responsible_devices() + tail
    return html


@application.route("/backlog_of_stats/<category>/<name>", methods=['get'])
def backlog_of_stats_category_name_(category: str, name: str) -> str:
    """
    1. html中にはモーダル有効化の<a>タグ中のフラグ(e.g. data-featherlight="image")が存在するので、取り除く
    2. htmlのbodyの中にスマホ用に画面にフィットさせるJSを注入する
    Args:
        - category: 統計的に処理した結果のどれがほしいか
        - name: 日付等を含んだ具体的な読み込むべきファイル名
    Retruns:
        - str: html
    """
    fn = f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/{category}_50000/htmls/{name}'
    with open(fn) as fp:
        html = fp.read()

    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", attrs={"data-featherlight": True}):
        del a["data-featherlight"]
    # print(BeautifulSoup(ResponsibleDevices.responsible_devices()))
    soup.find("body").insert(0, BeautifulSoup(ResponsibleDevices.responsible_devices(), "lxml"))
    return soup.__str__()



@application.route("/get_day/<day>", methods=['GET'])
def get_day(day):
    data = Base64EncodeDecode.string_base64_pickle(request.args['serialized'])
    return GetDay.get_day_html(day, data)


@application.route("/sitemap", methods=['GET'])
@application.route("/sitemap.txt", methods=['GET'])
def sitemap():
    with open(f'{TOP_DIR}/var/sitemap.txt') as fp:
        html = fp.read()
    return html


@application.route("/user_favorited_ranking", methods=['GET'])
def user_favorited_ranking():
    with open(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/user_favorited_ranking.html') as fp:
        html = fp.read()
    return html


@application.route("/daily_yj_ranking_list", methods=['GET'])
def daily_yj_ranking_list():
    return GenerateDailyYJRankingList.generate_daily_ranking_list()


@application.route("/backlog_of_twitter", methods=['get'])
def backlog_of_twitter():
    import glob

    head = '<html><head><title>backlog of twitter</title></head><body>'
    body = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/htmls/*'))):
        name = Path(fn).name
        date = name.replace(".html", "")
        tmp = f'''<a href="/backlog_of_twitter/{name}">{date}</a><br>'''
        body += tmp
    tail = '</body></html>'
    html = head + body + tail
    return html


@application.route("/backlog_of_twitter/<name>", methods=['get'])
def backlog_of_twitter_name(name):
    fn = f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/htmls/{name}'
    with open(fn) as fp:
        html = fp.read()
    return html


@application.route("/twitter/input/<day>/<digest>")
def twitter_input(day, digest):
    # print('input', day, digest)
    with open(f'{TOP_DIR}/var/Twitter/input/{day}/{digest}') as fp:
        html = fp.read()
    return html


@application.route("/twitter/tweet/<day>/<digest>")
def twitter_tweet(day, digest):
    print('tweet', day, digest)
    with open(f'{TOP_DIR}/var/Twitter/tweet/{day}/{digest}') as fp:
        html = fp.read()
    return html


@application.route("/twitter/<typed>/<digest>")
def twitter_(typed, digest):
    # print(digest)
    try:
        if typed in {'tweet', 'css', 'input'}:
            with open(f'{TOP_DIR}/var/Twitter/{typed}/{digest}') as fp:
                html = fp.read()
            return html
        elif typed in {'jpg', 'jpgs'}:
            with open(f'{TOP_DIR}/var/Twitter/jpgs/{digest}', 'rb') as fp:
                binary = fp.read()
            response = make_response(binary)
            response.headers.set('Content-Type', 'image/jpeg')
            return response
        elif typed in {'png', 'pngs'}:
            with open(f'{TOP_DIR}/var/Twitter/pngs/{digest}', 'rb') as fp:
                binary = fp.read()
            response = make_response(binary)
            response.headers.set('Content-Type', 'image/png')
            return response
    except Exception as exc:
        print(exc)
        return abort(404)


@application.route("/gyo")
def gyo():
    with open(f'{TOP_DIR}/var/Gyo/html') as fp:
        html = fp.read()
    return html


@application.route("/gyo2")
def gyo2():
    with open(f'{TOP_DIR}/var/Gyo/screenshot.png', 'rb') as fp:
        png = fp.read()
    response = make_response(png)
    response.headers.set('Content-Type', 'image/png')
    return response


@application.route("/blobs/<digest>", methods=['GET'])
def blobs(digest):
    if not Path(f'{TOP_DIR}/var/Gyo/blobs/{digest}').exists():
        return 'ng'

    with open(f'{TOP_DIR}/var/Gyo/blobs/{digest}', 'rb') as fp:
        data_type = pickle.loads(gzip.decompress(fp.read()))
    if data_type.type == bytes:
        response = make_response(data_type.data)
        response.headers.set('Content-Type', 'image/jpeg')
        return response
    elif data_type.type == str:
        return data_type.data
    return 'ok'


@application.route("/blobs_yj/<digest>", methods=['GET', "POST"])
def blobs_yj(digest: str) -> str:
    """
    Args:
        - digest: YahooNewsのハッシュ値
    Return:
        - str: html, 失敗したら失敗した内容を記述
    Posts:
        - YJSubmit: Submit
        - YJComment: str
            - コメントが有る場合、コメントををまず保存する
    """
    if request.method == 'POST':
        obj = request.form
        if obj.get("YJComment"):
            YJComment = obj["YJComment"]
            out_dir = f"{TOP_DIR}/var/YJ/YJComment/{digest}"
            Path(out_dir).mkdir(exist_ok=True, parents=True)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f"{out_dir}/{now}", "w") as fp:
                if twitter.authorized:
                    json.dump({"YJComment": YJComment, "datetime":now, "screen_name": twitter.token["screen_name"]}, fp, ensure_ascii=False)
                else:
                    json.dump({"YJComment": YJComment, "datetime":now, "screen_name": "名無しちゃん"}, fp, ensure_ascii=False)

    try:
        with open(f'{TOP_DIR}/var/Gyo/blobs/{digest}', 'rb') as fp:
            try:
                data_type = pickle.loads(gzip.decompress(fp.read()))
            except EOFError:
                Path(f'{TOP_DIR}/var/Gyo/blobs/{digest}').unlink()
                return 'ng.'
        if data_type.type == bytes:
            response = make_response(data_type.data)
            response.headers.set('Content-Type', 'image/jpeg')
            return response
        elif data_type.type == str:
            html = data_type.data
            return AdhocYJHtmlReplace.yj_html_replace(html, digest)
        return 'ok'
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)
        return "ng"


if __name__ == "__main__":
    application.run(host='0.0.0.0')
