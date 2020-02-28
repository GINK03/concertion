import os
from pathlib import Path
from os import environ as E
HOME = E.get('HOME')
HERE = Path(__file__).resolve().parent

def run():
    Path(f'{HERE}/var/favs').mkdir(exist_ok=True, parents=True)
    if not Path(f'{HERE}/var/favs').is_mount():
        for source, target in [(f'192.168.40.12:{HOME}/sda', f'{HERE}/var/favs')]:
            os.system(f'sshfs {source} {target}')