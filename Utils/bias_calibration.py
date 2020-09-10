from concurrent.futures import ProcessPoolExecutor
import requests
from pathlib import Path
import glob
import random
import pickle
import pandas as pd
import sys

try:
    sys.path.append("../Web")
    import GetFeatsOrMake
    import MakeRecommend
except Exception as exc:
    print(exc)
    exit()

if not Path("/tmp/user_dirs.pkl").exists():
    user_dirs = glob.glob((Path("~/.mnt/nfs/favs01").expanduser() / "*").__str__())
    with open("/tmp/user_dirs.pkl", "wb") as fp:
        pickle.dump(user_dirs, fp)
else:
    with open("/tmp/user_dirs.pkl", "rb") as fp:
        user_dirs = pickle.load(fp)

user_dirs = random.sample(user_dirs, 500)


def proc(user_dir):
    try:
        username = Path(user_dir).name
        GetFeatsOrMake.get(username)
        r = MakeRecommend.run(username)
        print(username)
        r = r.drop_duplicates(subset=["kigyo"], keep="first")
        r["rank"] = [len(r) - i for i in range(len(r))]
        return r[["kigyo", "rank"]]

    except Exception as exc:
        print(exc)
        return None


rs = []
with ProcessPoolExecutor(max_workers=12) as exe:
    for r in exe.map(proc, user_dirs):
        if r is None:
            continue
        rs.append(r)

if Path("rs.csv").exists():
    tmp = pd.read_csv("rs.csv")
    rs.append(tmp)
rs = pd.concat(rs).groupby(by=["kigyo"]).agg(rank=("rank", "sum")).reset_index()
rs.sort_values(by=["rank"], ascending=False, inplace=True)
rs.to_csv("rs.csv", index=None)
