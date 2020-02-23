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
    import A001_fetch
    import C001_collect_comment
    import D001_make_stats_and_make_csv
except Exception as exc:
    raise Exception(exc)


def run_suit():
    print('start to fetch data(A001_fetch).')
    if E.get('RESOURCE'):
        os.system('pkill chrome')
    start = time.time()
    try:
        A001_fetch.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'end to fetch data(A001_fetch), elapsed = {time.time() - start:0.02f}.')
    if E.get('RESOURCE'):
        os.system('pkill phamtomjs')
        os.system('pkill chrome')

    print('start to collect comment(C001_collect).')
    start = time.time()
    try:
        C001_collect_comment.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'end to collect comment(C001_collect), elapsed = {time.time() - start:0.02f}.')
    if E.get('RESOURCE'):
        os.system('pkill phamtomjs')
        os.system('pkill chrome')

    print('start to make stats(D001_make_stats).')
    start = time.time()
    try:
        D001_make_stats_and_make_csv.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'end to make stats(D001_make_stats), elapsed = {time.time() - start:0.02f}.')
    if E.get('RESOURCE'):
        os.system('pkill phamtomjs')
        os.system('pkill chrome')


def run():
    while True:
        run_suit()


if __name__ == '__main__':
    run()
