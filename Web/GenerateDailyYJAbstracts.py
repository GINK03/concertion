
import pandas as pd
from pathlib import Path
import glob
from collections import namedtuple
import sys
import datetime

try:
    FILE = Path(__file__)
    TOP_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(f'{TOP_DIR}')
    from Web.Structures import DayAndPath
    from Web import GetDigest
    from Web import Base64EncodeDecode
    from Web import Hostname
except Exception as exc:
    print(exc)
    raise Exception(exc)



def generate_daily_yj_abstracts(day) -> str:
    head = '<html><head></head><body>'
    inner = '' 
    
    for fn in sorted(glob.glob(f'{TOP_DIR}/var/YJ/ranking_stats_daily/{day}/*')):
        name = Path(fn).name.replace(".csv", "")
        inner += f'''<h2>{name}</h2>'''
        df = pd.read_csv(fn)[:20]
        for url, title, category, score in zip(df.url, df.title, df.category, df.score):
            tmp = f'''<a href="https://{Hostname.hostname()}/blobs_yj/{GetDigest.get_digest(url)}">[{category}] {title}</a>score:{score:0.03f}<br>'''
            inner += tmp

    tail= '</body></html>'
    return head + inner + tail


