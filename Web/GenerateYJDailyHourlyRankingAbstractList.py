
import pandas as pd
from pathlib import Path
import glob
from collections import namedtuple
import sys
import datetime

FILE = Path(__file__)
TOP_FOLDER = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web.Structures import DayAndPath
    from Web import GetDigest
    from Web import Base64EncodeDecode
    from Web import Hostname
except Exception as exc:
    raise Exception(f"[{FILE}] import error, exc = {exc}")


def generate_daily_rankin_list():
    day_and_paths = []
    for fn in glob.glob(f'{TOP_FOLDER}/var/TB/daily_ranking/*'):
        day = Path(fn).name
        path = Path(fn)
        day_and_path = DayAndPath(day=day, path=Base64EncodeDecode.pickle_base64_stringify(path))
        day_and_paths.append(day_and_path)
    day_and_paths = list(reversed(sorted(day_and_paths, key=lambda x: x.day)))
    return day_and_paths


def generate_yj_daily_houry_ranking_abstract_list() -> str:
    """
    YJのランキングリスト作成する
    Args:
        - nothing
    Returns:
        - str: 構築したHTML
    """
    inner = '' 
    top3_latest_fns = list(reversed(sorted(glob.glob(f'{TOP_FOLDER}/var/YJ/ranking_stats/*'))))[:3]
    for fn in top3_latest_fns:
        try:
            df = pd.read_csv(fn)
        except pd.errors.EmptyDataError:
            Path(fn).unlink()
            continue
        name = Path(fn).name
        tmp = ''
        parsed_name = name.replace(".csv", "")
        renamed_title = datetime.datetime.strptime(parsed_name, "%Y-%m-%d %H").strftime("%Y年%m月%d日 %H時")
        tmp += f'''<h3>Yahoo News ログ {renamed_title}</h3>'''
        # max13件に限定する
        df = df[:13]
        for url, title, category, score in zip(df.url, df.title, df.category, df.score):
            tmp += f'''<div style="font-size:small; white-space: nowrap;"><a href="https://{Hostname.hostname()}/blobs_yj/{GetDigest.get_digest(url)}" original="{url}">[{category}] {title}</a>score:{score:0.03f}</div>'''
        inner += tmp
    return inner


if __name__ == '__main__':
    # ここはテスト
    print(generate_daily_rankin_list())
    generate_daily_rankin_list_html()
