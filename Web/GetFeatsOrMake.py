import numpy as np
import pandas as pd
import json
from loguru import logger
from pathlib import Path
FOLLOWINGS = Path(f"~/.mnt/cache/followings/").expanduser()
EACH_TL = Path("~/.mnt/22/sdb/kigyo/kigyo/tmp/users/each_tl").expanduser()
USER_EXP = Path(f"~/.mnt/22/sdb/kigyo/kigyo/tmp/users/user_expansion/").expanduser()
IDF = json.load(Path(f"~/.mnt/22/sdb/kigyo/kigyo/tmp/idf.json").expanduser().open())


def get(user):
    if not Path(USER_EXP / f"{user}.gz").exists():
        if not (EACH_TL / f"{user}.gz").exists():
            logger.info(Path(EACH_TL / f"{user}.gz"))
            return None
        dfs = [pd.read_csv(EACH_TL / f"{user}.gz")]
        logger.info(Path(FOLLOWINGS / f"{user}"))
        for following in Path(FOLLOWINGS / f"{user}").glob("*"):
            f = pd.read_csv(following)
            f = f.sample(frac=1)[:1000]
            for ex_user in f.username:
                ex_user = ex_user.replace("@", "").lower()
                if not (EACH_TL / f"{ex_user}.gz").exists():
                    continue
                ex = pd.read_csv(EACH_TL / f"{ex_user}.gz")
                ex["f"] = ex["f"].apply(lambda x: 3 if x >= 3 else x)
                dfs.append(ex)
            break
        # 強調
        dfs[0]["f"] *= max(int(len(dfs)*0.1), 1)
        df = pd.concat(dfs)

        c = df.groupby(by=["t"])["f"].sum().reset_index()
        c["sample_size"] = len(dfs)
        c["record_size"] = len(c)
        c.sort_values(by=["f"], ascending=False, inplace=True)
        c = c[:3000]
        c["w"] = [f / IDF[t] for f, t in zip(c.f, c.t)]
        c.sort_values(by=["w"], ascending=False, inplace=True)

        c.to_csv(USER_EXP / f"{user}.gz", compression="gzip")

    tmp = pd.read_csv((USER_EXP / f"{user}.gz"), compression = "gzip")
    return tmp
