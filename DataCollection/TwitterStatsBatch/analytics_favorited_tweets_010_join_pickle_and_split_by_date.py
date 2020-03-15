import pickle
import pandas as pd
import glob
from collections import namedtuple
from pathlib import Path
from tqdm import tqdm
import json
from concurrent.futures import ProcessPoolExecutor

FILE = Path(__file__).name
NAME = FILE.replace(".py", "")
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__).resolve().parent.parent

Datum = namedtuple('Datum', ['link', 'date', 'time', 'tz', 'created_at'])

def shake_down(date_datum_freq):
    for date, datum_freq in date_datum_freq.items():
        # get top 1000
        datum_freq_list = sorted([(datum, freq) for datum, freq in datum_freq.items()], key=lambda x:x[1])[-1000:]
        datum_set = set([datum for datum, freq in datum_freq_list])
        for datum in list(datum_freq.keys()):
            if datum not in datum_set:
                del datum_freq[datum]

def run():

    date_datum_freq = {}
    for fn in tqdm(glob.glob(f'{HERE}/var/CountFreq/*.pkl')):
        for datum, freq in tqdm(pickle.load(open(fn, 'rb')).items(), desc=fn):
            #print(datum, freq)
            #if freq == 1:
            #    continue
            date = datum.date
            if date not in date_datum_freq:
                date_datum_freq[date] = {}
            datum_freq = date_datum_freq[date]
            if datum not in datum_freq:
                datum_freq[datum] = 0
            datum_freq[datum] += freq

        shake_down(date_datum_freq)

    for date, datum_freq in date_datum_freq.items():
        df = pd.DataFrame(list(datum_freq.keys()))
        
        df['freq'] = list(datum_freq.values())
        if len(df) <= 900:
            continue
        
        Path(f'{HERE}/var/{NAME}/{date}').mkdir(exist_ok=True, parents=True)
        df.sort_values(by=['freq'], ascending=False, inplace=True)
        df.to_csv(f'{HERE}/var/{NAME}/{date}/out.csv', index=None)

if __name__ == "__main__":
    run()
