import gzip
import pickle
from flask import Flask, request, jsonify, render_template, make_response, abort
from flask import redirect, url_for
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
    from Web import GetJQuery
    from Web import GetFeatsOrMake
    from Web import MakeRecommend
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


@application.route('/.well-known/acme-challenge/yes_i_have')
def yes_i_have():
    return "ok"


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

@application.route("/feat", methods=['get', "post"])
def feat() -> str:
    print(request.method)
    if request.method == "GET":
        user = request.args.get('user')
    elif request.method == "POST":
        user = request.form.get("user").lower()
        redirect(f"/feat?user={user}")

    head = f'<html><head><title>feat</title></head><body>'

    body = f"<p>{user}の特徴！</p>"
    body += f'<a href="/feat?user={user}">sharable link</a>'
    df_or_none = GetFeatsOrMake.get(user)
    if df_or_none is None:
        raise Exception("存在しません")
    tmp = df_or_none
    tmp = tmp[tmp["t"].apply(lambda x: "bit.ly" != x)]
    tmp = tmp.sort_values(by=["f"], ascending=False)[:2000].sort_values(by=["w"], ascending=False)
    tmp.drop(["Unnamed: 0", "f", "sample_size", "record_size"], axis=1, inplace=True)
    body += tmp.to_html(index=None, col_space=200)
    tail = '</body></html>'
    html = head + body + tail
    return html

@application.route("/kigyo", methods=['get', "post"])
def kigyo() -> str:
    if request.method == "GET":
        user = request.args.get('user')
    elif request.method == "POST":
        user = request.form.get("user").lower()
        redirect("/kigyo?user={user}")
    head = f'<html><head><title>kigyo</title></head><body>'
    body = f"<p>{user}さんのお勧め企業！</p>"
    body += f'<a href="/kigyo?user={user}">sharable link</a>'
    
    df_or_none = GetFeatsOrMake.get(user)
    if df_or_none is None:
        raise Exception("存在しません")
    tmp = MakeRecommend.run(user)
    # tmp = pd.read_csv(Path(f"~/.mnt/22/sdb/kigyo/kigyo/tmp/quering/users/{user}.csv.gz"), compression="gzip")
    kigyos = tmp.drop_duplicates(subset=["kigyo"], keep="last").kigyo
    buff = []
    for kigyo in kigyos:
        sliced = tmp[tmp.kigyo == kigyo]
        score = sliced.w.sum() * (10**6)
        sliced = sliced[:10]

        kigyo = sliced.iloc[0].kigyo
        if "Unnamed: 0" in sliced.columns:
            sliced.drop(["Unnamed: 0"], axis=1, inplace=True)
        body += f"<p>{kigyo}がお勧め, score = {score:0.04f}</p>"
        body += sliced.to_html(index=None, col_space=200)
    tail = '</body></html>'
    html = head + body + tail
    return html


@application.route('/recent_stats/<category>/<page_num>')
def recent_stats_(category: str, page_num: str) -> str:
    return recent_stats.recent_stats(category, page_num)


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
    soup = BeautifulSoup(html, "lxml")
    soup.find("head").insert(0, BeautifulSoup(GetJQuery.get_jquery(), "html.parser"))
    soup.find("body").insert(0, BeautifulSoup(ResponsibleDevices.responsible_devices(), "html.parser"))
    soup.find("body").insert(-1, BeautifulSoup(ResponsibleDevices.responsible_devices(), "html.parser"))
    return soup.__str__()


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
            with open(f'{TOP_DIR}/mnt/twitter_jpgs/{digest}', 'rb') as fp:
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


if __name__ == "__main__":
    application.run(host='0.0.0.0')
