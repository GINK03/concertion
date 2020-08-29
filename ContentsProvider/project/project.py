import gzip
import pickle
from flask import Flask, request, jsonify, render_template, make_response, abort
from flask import redirect, url_for, send_file
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
from loguru import logger

FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent.parent
application = Flask(__name__)
logger.add(TOP_DIR / f"var/log/main.log", rotation="500 MB")

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
    # from Web import TweetHyoron
    from Web import ResponsibleDevices
    from Web import GetJQuery
    from Web import GetFeatsOrMake
    from Web import MakeRecommend
    from Web import GetAllUserCSV
    # application.register_blueprint(TweetHyoron.tweet_hyoron)
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

logger.info(f'current hostname = {Hostname.hostname()}')

@application.route('/.well-known/acme-challenge/yes_i_have')
def yes_i_have():
    logger.info(f"ip={request.remote_addr}")
    return "ok"


@application.route("/")
def home() -> str:
    logger.info(f"ip={request.remote_addr}")
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
    logger.info(f"ip={request.remote_addr}")
    return Login.login()

@application.route("/feat", methods=['get', "post"])
def feat() -> str:
    logger.info(f"ip={request.remote_addr}")
    if request.method == "GET":
        user = request.args.get('user')
    elif request.method == "POST":
        user = request.form.get("user").lower()
        redirect(f"/feat?user={user}")

    head = f'<html><head><title>feat</title></head><body>'

    body = f"""<p><a href="https://twitter.com/{user}" target="_blaknk">{user}</a>の特徴!</p>"""
    body += f'<a href="/feat?user={user}">sharable link</a>'
    df_or_none = GetFeatsOrMake.get(user)
    if df_or_none is None:
        raise Exception("存在しません")
    tmp = df_or_none
    tmp = tmp[tmp["t"].apply(lambda x: "bit.ly" != x)]
    tmp = tmp.sort_values(by=["f"], ascending=False)[:2000].sort_values(by=["w"], ascending=False)
    tmp.drop(["Unnamed: 0", "f", "sample_size", "record_size"], axis=1, inplace=True)
    # 大きさのノーマライズ
    tmp["w"] /= tmp["w"].min()
    body += tmp.to_html(col_space=200)
    tail = '</body></html>'
    html = head + body + tail
    return html

@application.route("/kigyo", methods=['get', "post"])
def kigyo() -> str:
    logger.info(f"ip={request.remote_addr}")
    if request.method == "GET":
        user = request.args.get('user')
    elif request.method == "POST":
        user = request.form.get("user").lower()
        redirect("/kigyo?user={user}")
    head = f'<html><head><title>kigyo</title></head><body>'
    body = f"""<p> <a href="https://twitter.com/{user}" target="_blank">{user}</a>さんのお勧め企業！</p>"""
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
        score = int(sliced.w.sum() * (10))
        sliced = sliced[:10]

        kigyo = sliced.iloc[0].kigyo
        if "Unnamed: 0" in sliced.columns:
            sliced.drop(["Unnamed: 0"], axis=1, inplace=True)
        body += f"<p>{kigyo}がお勧め, score = {score}</p>"
        body += sliced.to_html(index=None, col_space=200)
    tail = '</body></html>'
    html = head + body + tail
    return html

@application.route('/get_all_csv')
def get_all_csv():
    logger.info(f"ip={request.remote_addr}")
    path = GetAllUserCSV.get_path()
    return send_file(path, as_attachment=True)


@application.route('/recent_stats/<category>/<page_num>')
def recent_stats_(category: str, page_num: str) -> str:
    logger.info(f"ip={request.remote_addr}")
    return recent_stats.recent_stats(category, page_num)


@application.route("/user_favorited_ranking", methods=['GET'])
def user_favorited_ranking():
    logger.info(f"ip={request.remote_addr}")
    with open(TOP_DIR / 'DataCollection/TwitterStatsBatch/var/user_favorited_ranking.html') as fp:
        html = fp.read()
    return html


if __name__ == "__main__":
    application.run(host='0.0.0.0')
