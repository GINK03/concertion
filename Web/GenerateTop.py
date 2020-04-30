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
    body += '<p><a href="/recent_uraaka">最近人気の裏垢</a>    <a href="/backlog_of_uraaka">過去の裏垢のバックログ</a></p>'
    body += '<p><a href="/recent_guradoru">最近人気のグラドル</a>    <a href="/backlog_of_guradoru">過去のグラドルのバックログ</a></p>'
    body += '<p><a href="/recent_corona">最近人気の同人</a>    <a href="/backlog_of_corona">過去の同人のバックログ</a></p>'
    body += '<p><a href="/recent_kawaii">最近人気の可愛い</a>    <a href="/backlog_of_kawaii">過去の可愛いのバックログ</a></p>'
    """ これはコンテンツの作り込みが薄くサスペンド """

    body += "</div><h3>過去ログ</h3>"
    body += '<p><a href="/daily_yj_ranking_list">過去Yahoo Newsで流行ったログ</a></p>'
    body += '<p><a href="/backlog_of_twitter">過去のツイッターのバックログ</a></p></div>'
    # twitter
    body += '<div class="twitter"><h3>最近のツイッター</h3>'
    body += GetBuzzTweet.get_buzz_tweet()
    body += '</div>'
    # yahoo
    body += '<div class="yj">'
    body += GenerateYJDailyHourlyRankingAbstractList.generate_yj_daily_houry_ranking_abstract_list()
    body += '</div>'

    body += '<div class="yj_daily_ranking">'
    body += '<h2>過去のYahoo Newsのログ</h2>'
    body += GenerateDailyYJRankingList.generate_daily_ranking_list()
    body += '</div>'
    return head + body + tail


if __name__ == '__main__':
    # here is single test
    html = get_buzz_tweet()
    print(html)
