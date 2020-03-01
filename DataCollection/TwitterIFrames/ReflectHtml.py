from lxml.html.clean import Cleaner
import warnings
import pandas as pd
import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import concurrent
import time
import glob
from pathlib import Path
import pickle
import sys
from urllib.parse import urlparse
import shutil
from bs4 import BeautifulSoup
import datetime
import requests
import glob
import re
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import base64

FILE = Path(__file__).name
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent
try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web.Structures import TitleUrlDigestScore
    from Web.Structures import YJComment
    from Web import QueryToDict
    from Web import GetDigest
except Exception as exc:
    raise Exception(exc)
warnings.simplefilter("ignore")

def get_file_content_chrome(driver, uri):
  result = driver.execute_async_script("""
    var uri = arguments[0];
    var callback = arguments[1];
    var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'arraybuffer';
    xhr.onload = function(){ callback(toBase64(xhr.response)) };
    xhr.onerror = function(){ callback(xhr.status) };
    xhr.open('GET', uri);
    xhr.send();
    """, uri)
  if type(result) == int :
    raise Exception("Request failed with status %s" % result)
  return base64.b64decode(result)

headers={'User-Anget':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.88 Safari/537.36'}
'''set html to path'''
# bla

def reflect_html(day:str, digest:str):
    '''get'''
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.add_argument("window-size=1024x2024")
    options.add_argument(f"user-data-dir=/tmp/{FILE.replace('.py', '')}")
    options.binary_location = shutil.which('google-chrome')
    driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
    driver.get(f'https://concertion.page/twitter/input/{day}/{digest}')
    time.sleep(2.0)

    html = driver.page_source

    '''get shadow-root'''
    elm = driver.execute_script('''return document.querySelector("twitter-widget").shadowRoot''')
    inner_html = elm.get_attribute('innerHTML')
    cleaner = Cleaner(  style=True, 
                        links=True, 
                        add_nofollow=True,
                        page_structure=False, 
                        safe_attrs_only=False)
    print(inner_html)
    soup = BeautifulSoup(inner_html, 'lxml')
    imported_csses = [el for el in soup.find_all('style', {'type': 'text/css'})]

    # replace css text to local css
    for css in imported_csses:
        if '@import url' in css.text:
            css_url = re.search(r'url\("(.*?)"\)', css.text).group(1)
            css_digest = GetDigest.get_digest(css_url)
            print(css_url, css_digest)
            with requests.get(css_url) as r:
                css_text = r.text
            Path(f'{TOP_FOLDER}/var/Twitter/css').mkdir(exist_ok=True, parents=True)
            with open(f'{TOP_FOLDER}/var/Twitter/css/{css_digest}', 'w') as fp:
                fp.write(css_text)
            css.string = f'@import url("/twitter/css/{css_digest}")'

    # replace image src
    for img in soup.find_all(attrs={'src':True}):
        url = img.get('src')
        o = urlparse(url)
        if o.scheme == '':
            o = o._replace(scheme='https')
        url = o.geturl()

        url_digest = GetDigest.get_digest(url)
        print('img url', url)
        if 'format=jpg' in url or re.search('.jpg$', url) or re.search('.jpeg$', url):
            with requests.get(url, timeout=3) as r:
                binary = r.content
            Path(f'{TOP_FOLDER}/var/Twitter/jpgs').mkdir(exist_ok=True, parents=True)
            with open(f'{TOP_FOLDER}/var/Twitter/jpgs/{url_digest}', 'wb') as fp:
                fp.write(binary)
            img['src'] = f'/twitter/jpgs/{url_digest}'
        elif 'format=png' in url or re.search('.png$', url):
            with requests.get(url, timeout=3) as r:
                binary = r.content
            Path(f'{TOP_FOLDER}/var/Twitter/pngs').mkdir(exist_ok=True, parents=True)
            with open(f'{TOP_FOLDER}/var/Twitter/pngs/{url_digest}', 'wb') as fp:
                fp.write(binary)
            img['src'] = f'/twitter/pngs/{url_digest}'
        else:
            raise Exception('unsupported image!')
    
    # try to download video
    # if PlayButton not exist, cannot do this.
    """
    elm.find_element_by_class_name('PlayButton').click()
    time.sleep(3.)
    for video in elm.find_elements_by_tag_name('iframe'):
        iframe_url = video.get_attribute('src')
        driver.switch_to.frame(video)
        print('video', iframe_url)
        video_html = driver.page_source
        print(video_html)
        video_soup = BeautifulSoup(video_html, 'lxml')
        blob_url = video_soup.find('video').get('src')
        print('blob_url', blob_url)
        binary = get_file_content_chrome(driver, blob_url)
        print('contents len', len(binary))
    """
    '''adhoc style edit'''
    soup.find(attrs={'class':'EmbeddedTweet'})['style'] = 'margin: 0 auto; margin-top: 150px;'
    
    out_dir = f'{TOP_FOLDER}/var/Twitter/tweet/{day}'
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    with open(f'{out_dir}/{digest}', 'w') as fp:
        fp.write(soup.__str__())

    return f'/twitter/tweet/{day}/{digest}'


def glob_fs_and_work():
    for fn in glob.glob(f'{TOP_FOLDER}/var/Twitter/input/*/*'):
        path = Path(fn)
        digest = path.name
        day = path.parent.name
        out_file = f'{TOP_FOLDER}/var/Twitter/tweet/{day}/{digest}'
        if Path(out_file).exists():
            continue
        try:
            print('digest day', digest, day)
            ret = reflect_html(day, digest)
            print('ret is', ret)
        except Exception as exc:
            print(exc)
if __name__ == '__main__':
    glob_fs_and_work()
