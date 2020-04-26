from pathlib import Path
import sys
FILE = Path(__file__).name
HERE = Path(__file__).resolve().parent
try:
    sys.path.append(f'{HERE}')
    import FetchRecentBuzzTweets
    import PutLocaHtml
    import ReflectHtml
except Exception as exc:
    raise Exception(f"import error {exc}")

def run():
    """
    最新の流行ったツイートを集計して表示できるようにする
    FetchRecentBuzzTweets.run() : 最新のfavsから最新のデータを用いて取得対象のリストを作成
    PutLocaHtml.read_csv_and_put_to_local() : 対象のリストからjsを動作してスクレイピング可能にするため、localの配信フォルダにプッシュ
    ReflectHtml.glob_fs_and_work() : 取得
    """
    FetchRecentBuzzTweets.run()

    PutLocaHtml.read_csv_and_put_to_local()

    ReflectHtml.glob_fs_and_work()


if __name__ == "__main__":
    run()
