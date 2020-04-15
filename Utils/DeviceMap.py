import os
from pathlib import Path
from os import environ as E
TOP_DIR = Path(__file__).resolve().parent.parent
HOME = E.get('HOME')

os.system(f'sshfs 127.0.0.1:{HOME}/sda/var {TOP_DIR}/var -o reconnect,nonempty')
# os.system(f'sshfs 192.168.40.16:{HOME}/sdd/matching.jp/var matching.jp -o reconnect')
