import datetime
import pickle
import gzip
from typing import Union, Optional
from typing import Tuple
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import shutil
import time
import sys

FILE = Path(__file__).name
NAME = Path(__file__).name.replace(".py", "")
PARENT = Path(__file__).resolve().parent.name
TOP_DIR = Path(__file__).resolve().parent.parent.parent
try:
    sys.path.append(f"{TOP_DIR}")
    from Libs import SignateRecord
    from Libs import SignateRecords
except Exception as exc:
    raise Exception(exc)


def get_html():
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1024x2024")
    options.add_argument(f"user-data-dir=/tmp/{NAME}")
    options.binary_location = shutil.which("google-chrome")
    driver = webdriver.Chrome(executable_path=shutil.which("chromedriver"), options=options)
    driver.get("https://signate.jp/competitions")
    time.sleep(2.0)
    html = driver.page_source
    return html


def get_text(soup):
    if soup:
        text = soup.text.strip()
        text = re.sub(r"[\s|\n]{1,}", " ", text)
        return text
    return None


def get_date_limit(text: str) -> Tuple[Union[str, None], Union[str, None]]:
    if mo:= re.search("(\d\d\d\d年\d{1,}月\d{1,}日)", text):
        limit_date: Optional[str] = mo.group(1)
    else:
        limit_date = None
    if mo:= re.search("(残り\d{1,}日)", text):
        remaining_date: Optional[str] = mo.group(1)
    else:
        remaining_date = None

    return (limit_date, remaining_date)


def run():
    html = get_html()

    soup = BeautifulSoup(html, "lxml")

    signate_records: SignateRecords = []  # type: ignore
    for a in soup.find_all("a", {"href": True}):
        card = a.find(attrs={"class": "card-item"})

        card_title = a.find(attrs={"class": "card-title"})
        if card_title is None:
            continue
        if card_title.find("span"):
            card_title.find("span").decompose()
        entrie_number = a.find(attrs={"class": "entrie-number"})
        prize = a.find(attrs={"class": "prize"})
        duedate = a.find(attrs={"class": "duedate"})
        url = a.get("href")
        title = get_text(card_title)
        prize = get_text(prize)
        limit_date, remaining_date = get_date_limit(get_text(duedate))
        signate_record = SignateRecord(title=title, prize=prize, url=url, limit_date=limit_date, remaining_date=remaining_date)
        signate_records.append(signate_record)

    now_date = datetime.datetime.now().strftime("%Y-%m-%d")
    out_dir = f"{TOP_DIR}/var/{PARENT}/{now_date}"
    Path(out_dir).mkdir(exist_ok=True, parents=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_filename = f"{out_dir}/{ts}.pkl.gz"
    with open(out_filename, "wb") as fp:
        fp.write(gzip.compress(pickle.dumps(signate_records)))


if __name__ == "__main__":
    run()
