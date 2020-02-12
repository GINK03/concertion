
from concurrent.futures import ProcessPoolExecutor as PPE
import os
from os import environ as E
import time
HOME = E['HOME']

if E.get('MOUNT_HOST'):
    MOUNT_HOST = E['MOUNT_HOST']
    DISK = 'sdb'
    PORT = '22'
else:
    MOUNT_HOST = '118.1.240.123'
    DISK = 'sdb'
    PORT = '22'

def DataCollectorDriver():
    os.system('python3 DataCollection/system/00_wrapper.py')

def ContentsProviderDriver():
    os.system('python3 ContentsProvider/00_wrapper.py')

def SshfsMount():
    while True:
        CMD = f'sshfs {MOUNT_HOST}:{HOME}/{DISK}/var var -o IdentityFile={HOME}/.ssh/id_github -o StrictHostKeyChecking=no -p {PORT} -o nonempty 2>&1 >/dev/null'
        os.system(CMD)
        time.sleep(10)

# 関数をバイパスして、実行するだけ
def Driver(func):
    func()

if __name__ == '__main__':

    funcs = [SshfsMount, DataCollectorDriver, ContentsProviderDriver]
    #funcs = [SshfsMount]
    with PPE(max_workers=16) as exe:
        exe.map(Driver, funcs)
