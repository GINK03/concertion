import gzip
import pickle
import datetime
import glob
from pathlib import Path
import sys
from typing import List

TOP_DIR = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f"{TOP_DIR}")
    from Libs import SignateRecords
    from Libs import SignateRecord
except Exception as exc:
    raise Exception(exc)


def generate_signate() -> str:
    # now_date = datetime.datetime.now().strftime("%Y-%m-%d")
    """
    ソートして最も後ろのdirが対象
    """
    date_dirs: List[str] = sorted(glob.glob(f"{TOP_DIR}/var/Signate/*"))
    date_dir: str = date_dirs[-1]

    ts_files: List[str] = sorted(glob.glob(f"{date_dir}/*"))
    ts_file: str = ts_files[-1]

    with open(ts_file, "rb") as fp:
        signate_records: SignateRecords = pickle.loads(gzip.decompress(fp.read()))

    """
    TOP 7を採用
    """
    html: str = ""
    for signate_record in signate_records[:7]:
        if signate_record.limit_date is None or signate_record.remaining_date is None:
            continue
        tmp: str = ""
        tmp += f"""
        <div style="font-size:small; white-space: nowrap;">
            <p><a target="_blank" href="{signate_record.url}">{signate_record.title}</a>, prize:{signate_record.prize}, dead:{signate_record.limit_date}, remain:{signate_record.remaining_date}</p>
        </div>
        """
        html += tmp
    return html

if __name__ == "__main__":
    html = generate_signate()
    print(html)
