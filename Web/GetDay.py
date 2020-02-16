import os
import sys
from pathlib import Path
import glob
import pandas as pd
FILE = Path(__file__).name
TOP_FOLDER = Path(__file__).resolve().parent.parent


def get_day(day, data):
    print(day, data)
    fn = data
    df = pd.read_csv(fn)
    return df


def get_day_html(day, data):
    df = get_day(day, data)
    
    head = '<html>' 
    tail = '</html>'
    body = ''
    '''PUB_DATE,TITLE,TWEET,ICON_VIEW,URL,TAGS'''
    df.sort_values(by=['ICON_VIEW'], ascending=False, inplace=True)
    for i in range(len(df)):
        title = df.iloc[i].TITLE
        icon_view = df.iloc[i].ICON_VIEW
        url = df.iloc[i].URL

        tmp = f'<p>{icon_view:012d}<a href={url}>{title}</a></p>'
        body += tmp

    return head + body + tail
