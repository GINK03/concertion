import pandas as pd
from pathlib import Path
import glob
from collections import namedtuple
import sys
import datetime
from bs4 import BeautifulSoup
from typing import Any
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter

    
FILE = Path(__file__)
TOP_FOLDER = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web import GenerateYJDailyHourlyRankingAbstractList
    from Web import GenerateDailyYJRankingList
    from Web.Structures import DayAndPath
    from Web import GetDigest
    from Web import Base64EncodeDecode
    from Web import Hostname
    from Web import GetBuzzTweet
except Exception as exc:
    tb_lineno = sys.exc_info()[2].tb_lineno
    raise Exception(f"[{FILE}] import error, exc = {exc}, tb_lineno = {tb_lineno}")


def generate_top(twitter: Any) -> str:
    """
    Args:
        - twitter: flask_danceによる認証情報、認証していないこともある
    Returns:
        - str: htmlをビルドして返却する
    """
    head = '''<html><head><title> Concertion Page </title>
    <style>
    .twitter {
        float: left;
        width: 500px;
        margin-left: 10px;
    }
    .yj {
        float: right;
        width: calc(100% - 500px - 20px);
        margin-left: 10px;
    }
    </style>
    </head>'''
    tail = '</html>'
    body = ''
    # titleとか
    body += '<h1>Concertion.Page SNS時代のバックログと評論</h1>'
    if not twitter.authorized:
        body += "<h3>ログインして便利に使おう</h3>"
        body += '<p><a href="/login">ログイン</a></p>'
    else:
        token = twitter.token
        screen_name = token['screen_name']
        body += f"<h3>こんにちは、{screen_name}さん</h3>"

    body += "<h3>統計的手法によりアカウント発見</h3>"
    body += '<p><a href="/recent_stats/裏垢女子/0">最近人気の裏垢</a>    <a href="/backlog_of_stats/裏垢女子">過去の裏垢のバックログ</a></p>'
    body += '<p><a href="/recent_stats/グラドル/0">最近人気のグラドル</a>    <a href="/backlog_of_stats/グラドル">過去のグラドルのバックログ</a></p>'
    body += '<p><a href="/recent_stats/同人/0">最近人気の同人</a>    <a href="/backlog_of_stats/同人">過去の同人のバックログ</a></p>'
    body += '<p><a href="/recent_stats/可愛い/0">最近人気の可愛い</a>    <a href="/backlog_of_stats/可愛い">過去の可愛いのバックログ</a></p>'
    """ これはコンテンツの作り込みが薄くサスペンド """

    body += "</div><h3>過去ログ</h3>"
    body += '<p><a href="/daily_yj_ranking_list">過去Yahoo Newsで流行ったログ</a></p>'
    body += '<p><a href="/backlog_of_twitter">過去のツイッターのバックログ</a></p></div>'
    # twitter
    body += f"""
    <div class="wrap">
        <div class="twitter"><h3>最近のツイッター</h3>'
            {GetBuzzTweet.get_buzz_tweet()}
        </div>
        <div class="yj">
            {GenerateYJDailyHourlyRankingAbstractList.generate_yj_daily_houry_ranking_abstract_list()}
        </div>
    </div>
    """

    # body += '<div class="yj_daily_ranking">'
    # body += '<h2>過去のYahoo Newsのログ</h2>'
    # body += GenerateDailyYJRankingList.generate_daily_ranking_list()
    # body += '</div>'
    return head + body + tail


if __name__ == '__main__':
    # here is single test
    html = get_buzz_tweet()
    print(html)
