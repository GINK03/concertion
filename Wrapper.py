
from concurrent.futures import ProcessPoolExecutor as PPE
import os
from os import environ as E
import time
from subprocess import Popen
from subprocess import PIPE
from pathlib import Path
import sys

HOME = E['HOME']
TOP_FOLDER = Path(__file__).resolve().parent
Path(f'{TOP_FOLDER}/var').mkdir(exist_ok=True)

if E.get('MOUNT_HOST') and E.get('MOUNT_PORT') and E.get('MOUNT_PATH'):
    MOUNT_HOST = E['MOUNT_HOST']
    MOUNT_PATH = E['MOUNT_PATH']
    MOUNT_PORT = E['MOUNT_PORT']
else:
    MOUNT_HOST = '127.0.0.1'
    MOUNT_PATH = '/home/gimpei/sdb/var'
    MOUNT_PORT = '32'

def DataCollectorDriver():
    try:
        sys.path.append(f'{TOP_FOLDER}/DataCollection/TogetterSystem')
        import Driver
        Driver.run()
    except Exception as exc:
        print(exc)
        raise Exception(exc)

def ContentsProviderDriver():
    try:
        sys.path.append(f'{TOP_FOLDER}/ContentsProvider')
        import GunicornWrapper
        GunicornWrapper.run()
    except Exception as exc:
        print(exc)
        raise Exception(exc)

def SshfsMount():
    print('try to mount sshfs...')
    while True:
        try:
            CMD = f'sshfs {MOUNT_HOST}:{MOUNT_PATH} var -o IdentityFile={HOME}/.ssh/id_github -o StrictHostKeyChecking=no -p {MOUNT_PORT} -o nonempty -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3'
            print(CMD)
            with Popen(CMD, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE) as proc:
                proc.communicate()
            time.sleep(10*10)
        except Exception as exc:
            print(exc)

# 関数をバイパスして、実行するだけ
def Driver(func):
    func()

if __name__ == '__main__':
    if '--mount' in sys.argv:
        funcs = [SshfsMount]
    elif '--data-collection' in sys.argv:
        funcs = [DataCollectorDriver]
    elif '--contents-provider' in sys.argv:
        funcs = [ContentsProviderDriver]
    else:
        funcs = [SshfsMount, DataCollectorDriver, ContentsProviderDriver]
    with PPE(max_workers=16) as exe:
        exe.map(Driver, funcs)
