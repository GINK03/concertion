import gzip
import pickle
from flask import Flask, request, jsonify, render_template, make_response, abort
import json
import requests
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import pandas as pd
from collections import namedtuple
import sys
import glob

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
    from Web import recent_uraaka
    from Web import recent_guradoru
    from Web import recent_corona
    from Web import recent_kawaii
except Exception as exc:
    print(exc)
    raise Exception(exc)

print(f'[{FILE}] {Hostname.hostname()}')


@application.route("/")
def home():
    return GenerateTop.generate_top()


@application.route('/daily_yj_abstracts/<name>')
def daily_yj_abstracts(name):
    return GenerateDailyYJAbstracts.generate_daily_yj_abstracts(name)


@application.route('/recent_uraaka')
def recent_uraaka_():
    return recent_uraaka.recent_uraaka()


@application.route('/recent_guradoru')
def recent_guradoru_():
    return recent_guradoru.recent_guradoru()


@application.route('/recent_corona')
def recent_corona_():
    return recent_corona.recent_corona()

@application.route('/recent_kawaii')
def recent_kawaii_():
    return recent_kawaii.recent_kawaii()

@application.route("/backlog_of_uraaka", methods=['get'])
def backlog_of_uraaka():
    head = '<html><head><title>backlog of uraaka</title></head><body>'
    body = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/裏垢女子_50000/htmls/*'))):
        name = Path(fn).name
        date = name.replace(".html", "")
        tmp = f'''<a href="/backlog_of_uraaka/{name}">{date}</a><br>'''
        body += tmp
    tail = '</body></html>'
    html = head + body + tail
    return html


@application.route("/backlog_of_uraaka/<name>", methods=['get'])
def backlog_of_uraaka_name(name):
    fn = f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/裏垢女子_50000/htmls/{name}'
    with open(fn) as fp:
        html = fp.read()
    return html

@application.route("/backlog_of_guradoru", methods=['get'])
def backlog_of_guradoru():
    head = '<html><head><title>backlog of guradoru</title></head><body>'
    body = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/グラドル_50000/htmls/*'))):
        name = Path(fn).name
        date = name.replace(".html", "")
        tmp = f'''<a href="/backlog_of_guradoru/{name}">{date}</a><br>'''
        body += tmp
    tail = '</body></html>'
    html = head + body + tail
    return html


@application.route("/backlog_of_guradoru/<name>", methods=['get'])
def backlog_of_guradoru_name(name):
    fn = f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/グラドル_50000/htmls/{name}'
    with open(fn) as fp:
        html = fp.read()
    return html

@application.route("/backlog_of_corona", methods=['get'])
def backlog_of_corona():
    head = '<html><head><title>backlog of corona</title></head><body>'
    body = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/同人_50000/htmls/*'))):
        name = Path(fn).name
        date = name.replace(".html", "")
        tmp = f'''<a href="/backlog_of_corona/{name}">{date}</a><br>'''
        body += tmp
    tail = '</body></html>'
    html = head + body + tail
    return html


@application.route("/backlog_of_corona/<name>", methods=['get'])
def backlog_of_corona_name(name):
    fn = f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/同人_50000/htmls/{name}'
    with open(fn) as fp:
        html = fp.read()
    return html

@application.route("/backlog_of_kawaii", methods=['get'])
def backlog_of_kawaii():
    head = '<html><head><title>backlog of kawaii</title></head><body>'
    body = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/可愛い_50000/htmls/*'))):
        name = Path(fn).name
        date = name.replace(".html", "")
        tmp = f'''<a href="/backlog_of_kawaii/{name}">{date}</a><br>'''
        body += tmp
    tail = '</body></html>'
    html = head + body + tail
    return html


@application.route("/backlog_of_kawaii/<name>", methods=['get'])
def backlog_of_kawaii_name(name):
    fn = f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/可愛い_50000/htmls/{name}'
    with open(fn) as fp:
        html = fp.read()
    return html


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
def twitter(typed, digest):
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


@application.route("/blobs_yj/<digest>", methods=['GET'])
def blobs_yj(digest):
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


if __name__ == "__main__":
    application.run(host='0.0.0.0')
