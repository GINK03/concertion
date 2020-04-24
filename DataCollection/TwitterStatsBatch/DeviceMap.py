import os
from pathlib import Path
from os import environ as E

HOME = E.get("HOME")
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__)


def run():
    for source, target in [
        (f"192.168.40.20:{HOME}/nvme0n1", f"{HOME}/.mnt/favs01"),
        (f"192.168.40.12:{HOME}/sda", f"{HOME}/.mnt/favs02"),
        (f"192.168.40.12:{HOME}/sdd", f"{HOME}/.mnt/favs03"),
    ]:
        if not Path(target).is_mount():
            Path(target).mkdir(exist_ok=True, parents=True)
            result = os.system(f"sshfs {source} {target} -o reconnect")
            print(f"mount result = {result}, on={target} from={source}")


if __name__ == "__main__":
    run()
