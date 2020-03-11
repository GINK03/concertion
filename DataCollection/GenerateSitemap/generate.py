import xml.etree.cElementTree as ET
import pandas as pd
import datetime
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

FILE = Path(__file__)
TOP_DIR = Path(__file__).resolve().parent.parent.parent

def run():
    urls = set()

    top = 'https://concertion.page'
    urls.add(top)
    with requests.get(top) as r:
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.find_all('a', {'href': re.compile(top)}):
            url = a.get('href')
            urls.add(url)

    twitter_top = 'https://concertion.page/backlog_of_twitter'
    urls.add(twitter_top)
    with requests.get(twitter_top) as r:
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.find_all('a', {'href': re.compile(top)}):
            url = a.get('href')
            urls.add(url)

    yj_backlog_top = 'https://concertion.page/daily_yj_ranking_list'
    urls.add(yj_backlog_top)
    with requests.get(yj_backlog_top) as r:
        tmp_urls = []
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.find_all('a', {'href': re.compile(top)}):
            url = a.get('href')
            tmp_urls.append(url)
    for tmp_url in tmp_urls:
        with requests.get(tmp_url) as r:
            soup = BeautifulSoup(r.text, 'lxml')
            for a in soup.find_all('a', {'href': re.compile(top)}):
                url = a.get('href')
                urls.add(url)


    with open(f'{TOP_DIR}/var/sitemap.txt', 'w') as fp:
        fp.write('\n'.join(list(urls)))


if __name__ == '__main__':
    run()
