
from pathlib import Path
import glob
from bs4 import BeautifulSoup

TOP_DIR = Path(__file__).resolve().parent.parent

def recent_stats(category: str, page_num:int) -> str:
    """
    1. DataCollection/TwitterStatsBatch/var/UraakaPickUp/recent.htmlからデータをロードする
    """
    if isinstance(page_num, str):
        page_num = int(page_num)
    with open(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/recents/recent_{category}_50000_{page_num}.html') as fp:
        html = fp.read()
    return html


