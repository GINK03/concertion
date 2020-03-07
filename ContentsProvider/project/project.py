import gzip
import pickle
from flask import Flask, request, jsonify, render_template, make_response
import json
import requests
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import pandas as pd
from collections import namedtuple
import sys
FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent.parent
application = Flask(__name__)

try:
    sys.path.append(f'{TOP_DIR}')
    from Web import Base64EncodeDecode
    from Web import GenerateTop
    from Web import AdhocYJHtmlReplace
    from Web.Structures import DayAndPath
    from Web import Hostname

    from Web import GetDay
    from Web import GenerateDailyYJAbstracts
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


@application.route("/get_day/<day>", methods=['GET'])
def get_day(day):
    data = Base64EncodeDecode.string_base64_pickle(request.args['serialized'])
    return GetDay.get_day_html(day, data)

@application.route("/user_favorited_ranking", methods=['GET'])
def user_favorited_ranking():
    with open(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/user_favorited_ranking.html') as fp:
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
    print(digest)
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
