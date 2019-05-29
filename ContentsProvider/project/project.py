from flask import Flask, request, jsonify, render_template, make_response
import json
import requests
from pathlib import Path
from datetime import datetime
from hashlib import sha256
import pandas as pd
from collections import namedtuple
application = Flask(__name__)

LOCAL_CSV = pd.read_csv('../../DataCollection/system/local.csv')
df = LOCAL_CSV.copy()

def filter_no_time(x):
    x = str(x)
    if len(x.split('-')) == 3:
        return True
    else:
        return False
def load_json(x):
    try:
        return json.loads(x)
    except:
        return None

df['PARSED_DATE'] = df['PUB_DATE'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d', errors='ignore'))
df = df[pd.notnull(df['PARSED_DATE'])]
df = df[df['PUB_DATE'].apply(filter_no_time)]
df['YEAR_WEEK_NUMBER'] = df['PARSED_DATE'].apply(lambda x:x.strftime('%Y %V'))
df['ICON_VIEW'] = df['ICON_VIEW'].apply(lambda x:int(x))
df['TAGS'] = df['TAGS'].apply(load_json)
df = df[pd.notnull(df['TAGS'])]

df['TITLE'] = df['TITLE'].apply(lambda x:x.replace(' - Togetter', ''))
df['YEAR'] = df['PUB_DATE'].apply(lambda x: str(x).split('-')[0])
df['MONTH'] = df['PUB_DATE'].apply(lambda x: str(x).split('-')[1])
df['YEAR_MONTH'] = df['PUB_DATE'].apply(
    lambda x: '-'.join(str(x).split('-')[0:2]))
df['YEAR_MONTH_DAY'] = df['PUB_DATE'].apply(
    lambda x: '-'.join(str(x).split('-')[0:3]))
#df['YEAR_WEEK_NUMBER'] = pd.to_datetime(df['PUB_DATE'], format='%Y-%m-%d').dt.strftime('%Y, %V')

def get_particle_data(PARTICLE_NAME='YEAR_MONTH', KEYWORD=None):
    Data = namedtuple('Data', ['URL', 'TITLE', 'ICON_VIEW', 'TAGS'])
    particle_data = {}
    if KEYWORD is None:
        dfTemp = df.copy()
    else:
        dfTemp = df[df['TAGS'].apply(lambda x: KEYWORD in x)]
    for PARTICLE, subDf in dfTemp.groupby(by=[PARTICLE_NAME]):
        subDf = subDf.sort_values(by=['ICON_VIEW'], ascending=False).head(10)
        for URL, TITLE, ICON_VIEW, TAGS in zip(subDf['URL'], subDf['TITLE'], subDf['ICON_VIEW'], subDf['TAGS']):
            if particle_data.get(PARTICLE) is None:
                particle_data[PARTICLE] = []
            particle_data[PARTICLE].append(Data(URL=URL, TITLE=TITLE, ICON_VIEW=ICON_VIEW, TAGS=TAGS))
    return list(reversed(sorted(particle_data.items(), key=lambda x:x[0])))

@application.route("/")
@application.route("/month")
def home():
    particle_data = get_particle_data(PARTICLE_NAME='YEAR_MONTH')
    r = render_template('home.html', particle_name='month', particle_data=particle_data)
    return r
@application.route("/month/<KEYWORD>")
def month_keyword(KEYWORD):
    particle_data = get_particle_data(PARTICLE_NAME='YEAR_MONTH', KEYWORD=KEYWORD)
    r = render_template('home.html', particle_name='month', particle_data=particle_data)
    return r

@application.route("/days")
def days():
    particle_data = get_particle_data(PARTICLE_NAME='YEAR_MONTH_DAY')
    r = render_template('home.html', particle_name='days', particle_data=particle_data)
    return r

@application.route("/days/<KEYWORD>")
def days_keyword(KEYWORD):
    particle_data = get_particle_data(PARTICLE_NAME='YEAR_MONTH_DAY', KEYWORD=KEYWORD)
    r = render_template('home.html', particle_name='days', particle_data=particle_data)
    return r

@application.route("/week")
def week():
    particle_data = get_particle_data(PARTICLE_NAME='YEAR_WEEK_NUMBER')
    r = render_template('home.html', particle_name='week', particle_data=particle_data)
    return r

@application.route("/week/<KEYWORD>")
def week_keyword(KEYWORD):
    particle_data = get_particle_data(PARTICLE_NAME='YEAR_WEEK_NUMBER', KEYWORD=KEYWORD)
    r = render_template('home.html', particle_name='week', particle_data=particle_data)
    return r

if __name__ == "__main__":
    application.run(host='0.0.0.0')
