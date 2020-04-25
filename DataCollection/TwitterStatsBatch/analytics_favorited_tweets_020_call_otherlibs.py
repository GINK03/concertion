import sys
from pathlib import Path

FILE = Path(__file__).name
HERE = Path(__file__).resolve().parent
PARENT = Path(__file__).resolve().parent.parent


try:
    sys.path.append(f"{PARENT}")
    import TwitterIFrames
except Exception as exc:
    print(f"[{FILE}] {exc}", file=sys.stderr)
    exit(256)


def run():
    TwitterIFrames.PutLocaHtml.read_csv_batch_backlog_and_put_to_local(f"{HERE}/var/analytics_favorited_tweets_010_join_pickle_and_split_by_date/")

    TwitterIFrames.ReflectHtml.glob_fs_and_work(NUM=500)


if __name__ == "__main__":
    run()
