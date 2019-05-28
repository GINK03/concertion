from flask import Flask, request, jsonify, render_template, make_response
import json
import requests
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import pandas as pd

application = Flask(__name__)

LOCAL_CSV = pd.read_csv('../../DataCollection/eda/local.csv')

@application.route("/")
def home():
    data = [(url, datum) for url, datum in data.items()]
    r = render_template('home.html', data=data)
    return r


if __name__ == "__main__":
    application.run(host='0.0.0.0')
