from pathlib import Path
import time

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
    try:
        A001_fetch.run()
    except Exception as exc:
        print(exc)

    try:
        C001_collect_comment.run()
    except Exception as exc:
        print(exc)

    try:
        D001_make_stats_and_make_csv.run()
    except Exception as exc:
        print(exc)

def run():
    while True:
        run_suit()

if __name__ == '__main__':
    run()
