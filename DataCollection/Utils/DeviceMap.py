import os
from pathlib import Path
from os import environ as E
TOP_DIR = Path(__file__).resolve().parent.parent
HOME = E.get('HOME')

def run():
    if not Path(f'{TOP_DIR}/var').is_mount():
        os.system(f"sshfs 127.0.0.1:{HOME}/sda/var {TOP_DIR}/var -o reconnect,nonempty -o ssh_command='ssh -i {HOME}/.ssh/id_github'")

if __name__ == "__main__":
    run()
