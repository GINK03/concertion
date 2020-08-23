from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import random
import numpy as np
import pandas as pd
import json
from pathlib import Path
import re
import pickle


NOISE = {"フルスペック", "ヤベェ", "スゲー", "クソワロタ", "ヤベー", "コロナ", "オッケー", "モック", "ステイホーム", "スミマセン", "ユニーク", "モチベ", "エクセル"}
KIGYO_DF = Path("~/.mnt/22/sdb/kigyo/kigyo/utils/draft_quering/kigyo_df.pkl").expanduser()
QUERING_USER = Path("~/.mnt/22/sdb/kigyo/kigyo/tmp/quering/users/").expanduser()
USER_EXP = Path(f"~/.mnt/22/sdb/kigyo/kigyo/tmp/users/user_expansion/").expanduser()

def norm_kigyo(df):
    df["weight"] /= df["freq"].max()
    for i in range(5):
        df["weight"] = np.log1p(df["weight"])
    tw = {t: w for t, w in zip(df["term"], df["weight"])}
    return tw


with open(KIGYO_DF, "rb") as fp:
    kigyos = pickle.load(fp)

def norm_user(df):
    df["w"] /= df["f"].max()
    for i in range(5):
        df["w"] = np.log1p(df["w"])
    tw = {t: w for t, w in zip(df["t"], df["w"])}
    return tw

def calc_rels(tw, kigyos):
    tmp = kigyos.copy()
    def _cal(ktw, index=0):
        same = set(ktw.keys()) & set(tw.keys())
        score = 0.0
        ts = {}
        for t in same:
            score += ktw[t] * tw[t]
            ts[t] = ktw[t] * tw[t]
        return [score, ts][index]

    tmp["score"] = tmp["tw"].apply(lambda x: _cal(x, 0))
    tmp["ts"] = tmp["tw"].apply(lambda x: _cal(x, 1))
    tmp.sort_values(by=["score"], ascending=False, inplace=True)
    ret = []
    for kigyo, ts in zip(tmp[:100].kigyo, tmp[:100].ts):
        ts = pd.DataFrame({"t": list(ts.keys()), "w": list(ts.values())})
        ts.sort_values(by=["w"], ascending=False, inplace=True)
        ts["kigyo"] = kigyo
        ret.append(ts)
    return pd.concat(ret)


def run(user):
    """
    Input:
        user
    """
    tmp = norm_user(pd.read_csv(USER_EXP / f"{user}.gz"))
    print(user)
    r = calc_rels(tmp, kigyos)
    print(r)
    #(TOP / "tmp/quering/users/").mkdir(exist_ok=True, parents=True)
    r.to_csv(QUERING_USER / f"{user}.gz", compression="gzip")
    return r
