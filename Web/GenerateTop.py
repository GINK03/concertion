import pandas as pd
from pathlib import Path
import glob
from collections import namedtuple
import sys
import datetime

try:
    FILE = Path(__file__)
    TOP_FOLDER = Path(__file__).resolve().parent.parent
    sys.path.append(f'{TOP_FOLDER}')
    from Web import GenerateYJDailyHourlyRankingAbstractList
    from Web import GenerateDailyYJRankingList
    from Web.Structures import DayAndPath
    from Web import GetDigest
    from Web import Base64EncodeDecode
    from Web import Hostname
except Exception as exc:
    print(exc)
    raise Exception(exc)

def get_buzz_tweet() -> str:
    """
    最新のtweetの取得リストから, 最新の取得したツイート(aka. 最後尾のツイート)を取得する
    """
    from bs4 import BeautifulSoup
    dir_fn = sorted(glob.glob(f'{TOP_FOLDER}/var/Twitter/tweet/*'))[-1]
    buzzes = []
    for idx, fn in enumerate(glob.glob(f'{dir_fn}/*')[-10:]):
        try:
            html = open(fn).read()
            soup = BeautifulSoup(html, features='lxml')
            div = soup.find('body').find('div')
            if div.find(attrs={'class':'EmbeddedTweet'}):
                div.find(attrs={'class':'EmbeddedTweet'})['style'] = 'margin-top: 10px; margin-left: 10px;'
            imagegrids = soup.find_all('a', {'class': 'ImageGrid-image'})
            for imagegrid in imagegrids:
                src = imagegrid.find('img').get('src')
                imagegrid['href'] = src
            mediaassets = soup.find_all('a', {'class': 'MediaCard-mediaAsset'})
            for mediaasset in mediaassets:
                if mediaasset.find('img') and mediaasset.find('img').get('alt') != 'Embedded video':
                    mediaasset['href'] = mediaasset.find('img').get('src')
            buzz_ctx = div.__str__()
            buzz_css = soup.find('body').find('style').__str__()
            buzzes.append(buzz_ctx + buzz_css)
        except Exception as exc:
            print(exc, file=sys.stderr)
    html = '\n'.join(buzzes)
    return html

def generate_top() -> str:
    head = '''<html><head><title> Concertion Page </title>
    </head>'''
    tail = '</html>'
    body = ''
    # titleとか
    body += '<h1>Concertion.Page SNS時代のバックログと評論</h1>'
    body += '<p><a href="/recent_uraaka">最近人気の裏垢</a></p>'
    body += '<p><a href="/backlog_of_uraaka">過去の裏垢のバックログ</a></p>'
    body += '<p><a href="/user_favorited_ranking">ツイッターでファボされた人ランキング</a></p>'
    body += '<p><a href="/daily_yj_ranking_list">過去Yahoo Newsで流行ったログ</a></p>'
    
    body += '<p><a href="/backlog_of_twitter">過去のツイッターのバックログ</a></p>'
    # twitter
    body += '<div class="twitter">'
    body += get_buzz_tweet()
    body += '</div>'
    # yahoo
    body += '<div class="yj">'
    body += GenerateYJDailyHourlyRankingAbstractList.generate_yj_daily_houry_ranking_abstract_list()
    body += '</div>'

    body += '<div class="yj_daily_ranking">'
    body += '<h2>過去のYahoo Newsのログ</h2>'
    body += GenerateDailyYJRankingList.generate_daily_ranking_list()
    body += '</div>'
    """
    # togetter
    day_and_paths: List[DayAndPath] = generate_daily_rankin_list()
    body += '<div class="togetter">'
    body += '<p>togetter backlog</p>'
    for day_and_path in day_and_paths:
        tmp = f'<a href="https://{Hostname.hostname()}/get_day/{day_and_path.day}?serialized={day_and_path.path}">{day_and_path.day}</a><br>'
        body += tmp
    body += "</div>"
    """
    return head + body + tail


if __name__ == '__main__':
    html = get_buzz_tweet()
    print(html)
