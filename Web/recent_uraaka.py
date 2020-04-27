
from pathlib import Path
import glob

TOP_DIR = Path(__file__).resolve().parent.parent

def recent_uraaka() -> str:
    """
    1. DataCollection/TwitterStatsBatch/var/UraakaPickUp/recent.htmlからデータをロードする
    """
    with open(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/recent_裏垢女子_50000.html') as fp:
        html = fp.read()
    return html


