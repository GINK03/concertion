from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import random
import numpy as np
import pandas as pd
import json
from pathlib import Path
import re
import pickle


TOP = Path(__file__).resolve().parent.parent

NOISY_KIGYO = set(pd.read_csv(Path(TOP / "var/NOISY_KIGYO.csv"))["kigyo"])
KIGYO_DF = Path("~/.mnt/22/sdb/kigyo/kigyo/utils/draft_quering/kigyo_df.pkl").expanduser()
QUERING_USER = Path("~/.mnt/22/sdb/kigyo/kigyo/tmp/quering/users/").expanduser()
USER_EXP = Path(f"~/.mnt/22/sdb/kigyo/kigyo/tmp/users/user_expansion/").expanduser()

rs_df = pd.read_csv(Path(TOP / "Utils/rs.csv"))
kigyo_rank = {kigyo: np.log1p(rank+1) for kigyo, rank in zip(rs_df.kigyo, rs_df["rank"])}

def norm_kigyo(df):
    df["weight"] /= df["freq"].max()
    for i in range(5):
        df["weight"] = np.log1p(df["weight"])
    tw = {t: w for t, w in zip(df["term"], df["weight"])}
    return tw

with open(KIGYO_DF, "rb") as fp:
    kigyos_df = pickle.load(fp)

kigyos_df = kigyos_df[kigyos_df.kigyo.apply(lambda x:x not in NOISY_KIGYO)]

def norm_user(df):
    df["w"] /= df["f"].max()
    for i in range(5):
        df["w"] = np.log1p(df["w"])
    tw = {t: w for t, w in zip(df["t"], df["w"])}
    return tw

def calc_rels(tw, kigyos_df):
    tmp = kigyos_df.copy()

    def _cal(ktw, kigyo, index=0):
        same = set(ktw.keys()) & set(tw.keys())
        scores = []
        ts = {}
        for t in same:
            if kigyo_rank.get(kigyo) is None:
                scores.append( ktw[t] * tw[t] )
            else:
                scores.append( ktw[t] * tw[t] / kigyo_rank[kigyo] )


        scores.sort()
        if len(scores) >= 5:
            th = scores[-5]
        else:
            th = 0
        score = 0.0
        for t in same:
            if kigyo_rank.get(kigyo) is None:
                s = ktw[t] * tw[t]
            else:
                s = ktw[t] * tw[t] / kigyo_rank[kigyo]
            if th >= s:
                score += s 
                ts[t] = s
            else:
                score += th
                ts[t] = th
        return [score, ts][index]
    generator = np.frompyfunc(_cal, 3, 1)

    tmp["score"] = generator(tmp["tw"].values, tmp["kigyo"].values, [0]*len(tmp)) #.apply(lambda x: _cal(x.tw, x.kigyo, 0), axis=1)
    tmp["ts"] = generator(tmp["tw"].values, tmp["kigyo"].values, [1]*len(tmp)) #.apply(lambda x: _cal(x.tw, x.kigyo, 1), axis=1)
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
    r = calc_rels(tmp, kigyos_df)
    print(r)
    #(TOP / "tmp/quering/users/").mkdir(exist_ok=True, parents=True)
    r.to_csv(QUERING_USER / f"{user}.gz", compression="gzip")
    return r
