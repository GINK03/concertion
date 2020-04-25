import glob
from pathlib import Path
import shutil
import sys

FILE = Path(__file__).name

def run():
    """
    tmpディレクトリも書き込み数が有限であるのであまりに書き込むとOSがクラッシュする。
    定期的にchromeなどの一時ファイルをクリアする
    """
    for fn in glob.glob(f"/tmp/*") + glob.glob(f"/tmp/.*"):
        is_dir = Path(fn).is_dir()
        stat = Path(fn).stat()
        if "C001_collect_comment" in fn or "Gyotaku.py" in fn or ".com.google.Chrome" in fn or "ReflectHtml" in fn:
            if is_dir:
                try:
                    shutil.rmtree(fn)
                except OSError as exc:
                    print(exc, file=sys.stderr)
                continue
            else:
                try:
                    Path(fn).unlink()
                except Exception as exc:
                    print(f'[{FILE}] exc = {exc}', file=sys.stderr)
                continue


if __name__ == "__main__":
    run()
