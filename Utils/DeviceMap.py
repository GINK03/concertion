import os
from pathlib import Path
from os import environ as E

TOP_DIR = Path(__file__).resolve().parent.parent
HOME = E.get("HOME")


def run():
    if not Path(f"{TOP_DIR}/var").is_mount():
        os.system(f"sshfs 127.0.0.1:{HOME}/sda/var {TOP_DIR}/var -o reconnect,nonempty -o ssh_command='ssh -i {HOME}/.ssh/id_github'")

    for source, target in [
        (f"192.168.40.20:{HOME}/nvme0n1", f"{HOME}/.mnt/favs01"),
        (f"192.168.40.12:{HOME}/sda", f"{HOME}/.mnt/favs02"),
        (f"192.168.40.12:{HOME}/sdd", f"{HOME}/.mnt/favs03"),
        (f"192.168.40.12:{HOME}/sdc", f"{HOME}/.mnt/favs04"),
        (f"127.0.0.1:{HOME}/sdc/TwitterImages/jpgs", f"{TOP_DIR}/mnt/twitter_jpgs"),
        (f"127.0.0.1:{HOME}/var", f"{TOP_DIR}/var"),
    ]:
        if not Path(target).is_mount():
            Path(target).mkdir(exist_ok=True, parents=True)
            result = os.system(f"sshfs {source} {target} -o reconnect")
            print(f"mount result = {result}, on={target} from={source}")


if __name__ == "__main__":
    run()
