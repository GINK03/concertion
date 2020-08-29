import pandas as pd
from pathlib import Path

from loguru import logger

logger.info("start to load csv")
ALL_USER = Path("~/.mnt/20/sda/matching.jp/var/CollectUsernameFromFavorites.csv").expanduser()

SIZE = 0
for line in ALL_USER.open():
    SIZE += 1

logger.info(f"end to load csv, SIZE={SIZE}")

def get_path() -> Path:
    return ALL_USER

def get_user_length() -> int:
    return SIZE

