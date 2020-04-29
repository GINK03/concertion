
from pathlib import Path
import glob

TOP_DIR = Path(__file__).resolve().parent.parent

def recent_corona() -> str:
    """
    1. DataCollection/TwitterStatsBatch/var/UraakaPickUp/recent.htmlからデータをロードする
    """
    with open(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/recent_同人_50000.html') as fp:
        html = fp.read()
    return html


