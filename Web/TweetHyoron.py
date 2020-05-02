
import gzip
import pickle
from flask import Flask, request, jsonify, render_template, make_response, abort
from flask import Blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
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


TOP_DIR = Path(__file__).resolve().parent.parent
FILE = Path(__file__).name

tweet_hyoron = Blueprint('tweet_hyoron', __name__, template_folder='templates')
@tweet_hyoron.route("/TweetHyoron/<day_name>/<digest>", methods=['get', "POST"])
def tweet_hyoron_(day_name:str, digest: str) -> str:
    """
    Args:
        - day_name: digestは<day_name>のフォルダごとに分類されている(冗長かもしれない)
        - digest: Twitterの評論対象のdigest
    Returns:
        - html: HTML
    POSTs:
        - TweetComment: str
    """
    if request.method == 'POST':
        obj = request.form
        if obj.get("TweetComment"):
            TweetComment = obj["TweetComment"]
            out_dir = f"{TOP_DIR}/var/Twitter/TweetComment/{digest}"
            Path(out_dir).mkdir(exist_ok=True, parents=True)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(f"{out_dir}/{now}", "w") as fp:
                if twitter.authorized:
                    json.dump({"TweetComment": TweetComment, "datetime":now, "screen_name": twitter.token["screen_name"]}, fp, ensure_ascii=False)
                else:
                    json.dump({"TweetComment": TweetComment, "datetime":now, "screen_name": "名無しちゃん"}, fp, ensure_ascii=False)
    head = '<html><head><title>Twitter評論</title></head><body>'
    body = ''
    with open(f'{TOP_DIR}/var/Twitter/tweet/{day_name}/{digest}') as fp:
        html = fp.read()
    soup = BeautifulSoup(html, features='lxml')
    div = soup.find('body').find('div')
    if div.find(attrs={'class': 'EmbeddedTweet'}):
        div.find(attrs={'class': 'EmbeddedTweet'})["style"] = "margin: 0 auto; margin-top: 30px;"
    imagegrids = soup.find_all('a', {'class': 'ImageGrid-image'})
    for imagegrid in imagegrids:
        src = imagegrid.find('img').get('src')
        imagegrid['href'] = src
    mediaassets = soup.find_all('a', {'class': 'MediaCard-mediaAsset'})
    for mediaasset in mediaassets:
        if mediaasset.find('img') and mediaasset.find('img').get('alt') != 'Embedded video':
            mediaasset['href'] = mediaasset.find('img').get('src')

    comment_html = f"""
    <form action="/TweetHyoron/{day_name}/{digest}" class="form" method="post" style="position: relative;"><textarea value="コメント" name="TweetComment" cols="55" rows="5" id="TweetComment" style="width: 65%; margin: 0 auto; margin-left:15%; margin-top: 10px;" ></textarea><br/>
    <input type="submit" name="TweetSubmit" value="Submit" style="-webkit-appearance: none;-webkit-border-radius: 4px;-moz-border-radius: 4px;-ms-border-radius: 4px;-o-border-radius: 4px;border-radius: 4px;-webkit-background-clip: padding;-moz-background-clip: padding;margin: 0;padding: 3px 10px;text-shadow: white 0 1px 1px;text-decoration: none;vertical-align: top;width: auto; margin-left:15%;">
    </from>
    """
    buzz_css = soup.find('body').find('style').__str__() if soup.find('body').find('style') else ""
    """
    Tweetのコメントをパース
    TODO: 要デザイン
    TODO: 要外だし
    """
    comments = []
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/var/Twitter/TweetComment/{digest}/*'))):
        try:
            obj = json.load(open(fn))
            comment = f'''<div class="TweetComment">
                <p>{obj["screen_name"]}</p><br/>
                <p>{obj["datetime"]}</p><br/>
                <p>{obj["TweetComment"]}</p><br/>
            </div>'''
            comments.append(comment)
        except Exception as exc:
            print(f"[{FILE}] exc = {exc}", file=sys.stderr)
            Path(fn).unlink()
    other_comments_html = "".join(comments)
    body += div.__str__() + buzz_css + comment_html + other_comments_html
    tail = '</body></html>'
    html = head + body + tail
    return html

