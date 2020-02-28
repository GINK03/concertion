from pathlib import Path
import time
from inspect import currentframe, getframeinfo
import os
from os import environ as E
FILE = Path(__file__).name
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__).resolve().parent.parent.parent

try:
    import sys
    sys.path.append(f'{HERE}')
    import TwitterIFrames
    import YahooJapanSystem
except Exception as exc:
    raise Exception(exc)

def release_resource():
    os.system('pgrep phamtomjs | xargs kill -9')
    os.system('pgrep chromedriver | xargs kill -9')
    os.system('pgrep chrome | xargs kill -9')

def run_suit():
    try:
        TwitterIFrames.DeviceMap.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    
    try:
        TwitterIFrames.FetchRecentBuzzTweets.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)

    try:
        TwitterIFrames.PutLocaHtml.read_csv_and_put_to_local()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    
    try:
        TwitterIFrames.ReflectHtml.glob_fs_and_work()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    
    release_resource()
    print('start to fetch data(A001_fetch).')
    start = time.time()
    try:
        YahooJapanSystem.A001_fetch.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'end to fetch data(A001_fetch), elapsed = {time.time() - start:0.02f}.')
    release_resource()

    print('start to collect comment(C001_collect).')
    start = time.time()
    try:
        YahooJapanSystem.C001_collect_comment.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'end to collect comment(C001_collect), elapsed = {time.time() - start:0.02f}.')
    release_resource()

    print('start to make stats(D001_make_stats).')
    start = time.time()
    try:
        YahooJapanSystem.D001_make_stats_and_make_csv.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'end to make stats(D001_make_stats), elapsed = {time.time() - start:0.02f}.')
    release_resource()


def run():
    while True:
        run_suit()


if __name__ == '__main__':
    run()
