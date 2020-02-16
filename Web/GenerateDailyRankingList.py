
import pandas as pd
from pathlib import Path
import glob
from collections import namedtuple
import sys

try:
    FILE = Path(__file__)
    TOP_FOLDER = Path(__file__).resolve().parent.parent
    sys.path.append(f'{TOP_FOLDER}')
    from Web.Structures import DayAndPath
    from Web import GetDigest
    from Web import Base64EncodeDecode
    from Web import Hostname
except Exception as exc:
    print(exc)
    raise Exception(exc)


def generate_daily_rankin_list():
    day_and_paths = []
    for fn in glob.glob(f'{TOP_FOLDER}/var/TB/daily_ranking/*'):
        day = Path(fn).name
        path = Path(fn)
        day_and_path = DayAndPath(day=day, path=Base64EncodeDecode.pickle_base64_stringify(path))
        day_and_paths.append(day_and_path)
    day_and_paths = list(reversed(sorted(day_and_paths, key=lambda x: x.day)))
    return day_and_paths


def generate_yj_daily_houry_ranking_list() -> str:
   
    inner = '' 
    for fn in reversed(sorted(glob.glob(f'{TOP_FOLDER}/var/YJ/ranking_stats/*'))):
        df = pd.read_csv(fn)
        name = Path(fn).name
        tmp = ''
        tmp += f'''<h3>{name}</h3>'''
        
        for url, title, category, score in zip(df.url, df.title, df.category, df.score):
            tmp += f'''<a href="http://{Hostname.hostname()}/blobs_yj/{GetDigest.get_digest(url)}">[{category}] {title}</a>score:{score:0.03f}<br>'''
        inner += tmp
    return inner


def generate_daily_rankin_list_html():
    head = '<html><head><title> ranking </title></head>'
    tail = '</html>'
    body = ''
    # yahoo
    body += '<div class="yj">'
    body += generate_yj_daily_houry_ranking_list()
    body += '</div>'

    # togetter
    day_and_paths: List[DayAndPath] = generate_daily_rankin_list()
    body += '<div class="togetter">'
    body += '<p>togetter backlog</p>'
    for day_and_path in day_and_paths:
        tmp = f'<a href="http://{Hostname.hostname()}/get_day/{day_and_path.day}?serialized={day_and_path.path}">{day_and_path.day}</a><br>'
        body += tmp
    body += "</div>"
    return head + body + tail


if __name__ == '__main__':
    print(generate_daily_rankin_list())
    generate_daily_rankin_list_html()
