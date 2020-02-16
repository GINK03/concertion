import pandas as pd
import glob
from pathlib import Path
import pickle
import sys
FILE = Path(__file__).name
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent
try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web.Structures import TitleUrlDigestScore
except Exception as exc:
    raise Exception(exc)

INPUT_FOLDER = f'{TOP_FOLDER}/var/YJ/frequency_watch/'


objs = []
for fn0 in glob.glob(f'{INPUT_FOLDER}/*'):
    for fn1 in glob.glob(f'{fn0}/*.pkl'):
        title_url_digest_score = pickle.load(open(fn1, 'rb'))
        objs.append(title_url_digest_score)

df = pd.DataFrame(objs)

print(df.columns)

objs = []
for (url, category), sub in df.groupby(by=['url', 'category']):
    print(url, category, sub.iloc[0].title)
    print(sub.score.sum())
    print(sub.date.min())
    obj = {'url': url, 'title':sub.iloc[0].title, 'category': category, 'score': sub.score.sum(), 'first_date': sub.date.min()}
    objs.append(obj)

df = pd.DataFrame(objs)

df['yyyy-mm-dd hh'] = df.first_date.apply(lambda x:x.strftime('%Y-%m-%d %H'))

OUT_DIR = f'{TOP_FOLDER}/var/YJ/ranking_stats'
Path(OUT_DIR).mkdir(exist_ok=True, parents=True)

for day_hour, sub in df.groupby('yyyy-mm-dd hh'):
    sub = sub.copy()
    sub.sort_values(by=['score'], inplace=True, ascending=False)
    sub.to_csv(f'{OUT_DIR}/{day_hour}.csv', index=None)
