
from concurrent.futures import ProcessPoolExecutor as PPE
import os



def DataCollectorDriver():
    os.system('python3 DataCollection/system/00_wrapper.py')
def ContentsProviderDriver():
    os.system('python3 ContentsProvider/00_wrapper.py')

# 関数をバイパスして、実行するだけ
def Driver(func):
    func()

if __name__ == '__main__':
    funcs = [DataCollectorDriver, ContentsProviderDriver]
    with PPE(max_workers=16) as exe:
        exe.map(Driver, funcs)
