
from concurrent.futures import ProcessPoolExecutor as PPE
import os
from os import environ as E
import time
from subprocess import Popen
from subprocess import PIPE
from pathlib import Path

HOME = E['HOME']
TOP_FOLDER = Path(__file__).resolve().parent
Path(f'{TOP_FOLDER}/var').mkdir(exist_ok=True)

if E.get('MOUNT_HOST'):
    MOUNT_HOST = E['MOUNT_HOST']
    DISK = 'sdb'
    PORT = '22'
else:
    MOUNT_HOST = '[240d:1a:d2:500:7285:c2ff:fe39:a811]'
    DISK = 'sdb'
    PORT = '22'

def DataCollectorDriver():
    os.system('python3 DataCollection/system/00_wrapper.py')

def ContentsProviderDriver():
    os.system('python3 ContentsProvider/00_wrapper.py')

def SshfsMount():
    while True:
        CMD = f'sshfs {MOUNT_HOST}:{HOME}/{DISK}/var var -o IdentityFile={HOME}/.ssh/id_github -o StrictHostKeyChecking=no -p {PORT} -o nonempty -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3'
        print(CMD)
        with Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
            proc.communicate()
        time.sleep(10*10)

# 関数をバイパスして、実行するだけ
def Driver(func):
    func()

if __name__ == '__main__':

    funcs = [SshfsMount, DataCollectorDriver, ContentsProviderDriver]
    #funcs = [SshfsMount]
    with PPE(max_workers=16) as exe:
        exe.map(Driver, funcs)
