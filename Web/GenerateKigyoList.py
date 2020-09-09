
from pathlib import Path
import re
import pandas as pd
import numpy as np

TOP = Path(__file__).resolve().parent.parent
def get() -> str:
    """
    Args: 
        - 
    Returns:
        - HTMLを返す
    """
    KIGYO_DIR = Path("~/.mnt/22/sdb/kigyo/kigyo/tmp/kigyos_filters").expanduser()
    NOISY_KIGYO = TOP / "var/NOISY_KIGYO.csv"
    noisy = set(pd.read_csv(NOISY_KIGYO).kigyo.tolist())
    head = f'<html><head><title>企業リスト</title></head><body>'
    body = ""


    tmp = []
    for feat_csv in KIGYO_DIR.glob("*.csv"):
        kigyo = re.sub(".csv$", "", feat_csv.name)
        entity =  f'<div><a href="/kigyo_feat?kigyo={kigyo}">{kigyo}</a></div>'
        tmp.append((kigyo, entity))
    a = pd.DataFrame(tmp).sort_values(by=0)
    a.columns = ["kigyo", "entity"]
    a = a[a.kigyo.apply(lambda x:x not in noisy)]
    for a0 in a["entity"]:
        body += a0

    tail = '</body></html>'
    html = head + body + tail
    return html
