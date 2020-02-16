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
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent
application = Flask(__name__)

try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web import Base64EncodeDecode
    from Web import GenerateDailyRankingList
    from Web import GetDay
    from Web import AdhocYJHtmlReplace
    from Web.Structures import DayAndPath
    from Web import Hostname
except Exception as exc:
    print(exc)
    raise Exception(exc)

print(Hostname.hostname())
@application.route("/")
def home():
    return GenerateDailyRankingList.generate_daily_rankin_list_html()


@application.route("/get_day/<day>", methods=['GET'])
def get_day(day):
    data = Base64EncodeDecode.string_base64_pickle(request.args['serialized'])
    return GetDay.get_day_html(day, data)


@application.route("/gyo")
def gyo():
    with open(f'{TOP_FOLDER}/var/Gyo/html') as fp:
        html = fp.read()
    return html


@application.route("/gyo2")
def gyo2():
    with open(f'{TOP_FOLDER}/var/Gyo/screenshot.png', 'rb') as fp:
        png = fp.read()
    response = make_response(png)
    response.headers.set('Content-Type', 'image/png')
    return response


@application.route("/blobs/<digest>", methods=['GET'])
def blobs(digest):
    if not Path(f'{TOP_FOLDER}/var/Gyo/blobs/{digest}').exists():
        return 'ng'
    
    with open(f'{TOP_FOLDER}/var/Gyo/blobs/{digest}', 'rb') as fp:
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
    with open(f'{TOP_FOLDER}/var/Gyo/blobs/{digest}', 'rb') as fp:
        data_type = pickle.loads(gzip.decompress(fp.read()))
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
