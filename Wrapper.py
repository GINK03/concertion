
from concurrent.futures import ProcessPoolExecutor as PPE
import os



def DataCollectorDriver():
    os.system('cd DataCollection/system && python3 00_wrapper.py')
def ContentsProviderDriver():
    os.system('cd ContentsProvider && python3 00_wrapper.py')
def Master(func):
    func()

if __name__ == '__main__':
    funcs = [DataCollectorDriver, ContentsProviderDriver]
    with PPE(max_workers=16) as exe:
        exe.map(Master, funcs)
