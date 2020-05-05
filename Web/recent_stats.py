
from pathlib import Path
import glob
from bs4 import BeautifulSoup
import sys

TOP_DIR = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f"{TOP_DIR}")
    from Web import ResponsibleDevices
except Exception as exc:
    raise Exception(exc)

def recent_stats(category: str, page_num:int) -> str:
    """
    1. DataCollection/TwitterStatsBatch/var/UraakaPickUp/recent.htmlからデータをロードする
    2. コンテンツを画面にフィットさせるためにJSが必要でそれを読み込むために、soupも必要
    """
    if isinstance(page_num, str):
        page_num = int(page_num)
    with open(f'{TOP_DIR}/DataCollection/TwitterStatsBatch/var/UraakaPickUp/recents/recent_{category}_50000_{page_num}.html') as fp:
        html = fp.read()
    soup = BeautifulSoup(html, "lxml")
    # print(BeautifulSoup(ResponsibleDevices.responsible_devices(), "lxml"))
    soup.find("body").insert(0, BeautifulSoup(ResponsibleDevices.responsible_devices(), "lxml"))
    return soup.__str__()


