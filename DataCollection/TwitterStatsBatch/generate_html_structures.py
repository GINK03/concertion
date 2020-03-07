import glob
from pathlib import Path
import pandas as pd
import datetime
from tqdm import tqdm
FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().name
print(FILE, TOP_DIR)

for fn in tqdm(glob.glob(f'{TOP_DIR}/var/twitter_batch_backlogs/*/*.csv')):
    path = Path(fn)
    date = path.parent.name
    df = pd.read_csv(fn)
    df['ts'] = df.apply(lambda x: x['date'] + ' ' + x['time'], axis=1)
    df['ts'] = df['ts'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df['hour'] = df['ts'].dt.hour

    oneday_tweets = ''
    for hour, sub in df.groupby(by=['hour']):
        sub = sub.copy()
        hour_tweets = ''
        hour_tweets += f'<h2>{date} {hour}時</h2>\n'
        sub.sort_values(by=['freq'], ascending=False, inplace=True)
        # print(sub)
        for link, freq in zip(sub.link, sub.freq):
            shot_tweet = ''
            shot_tweet += f'<p>Freq {freq}</p>\n'
            shot_tweet += f'''<blockquote class="twitter-tweet"><p lang="ja" dir="ltr">context <a href="{link}"> </a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>\n'''
            hour_tweets += shot_tweet
        oneday_tweets += hour_tweets
    # print(oneday_tweets)
    head = f'<html><head><title>{date}</title></head>'
    body = f'<body>{oneday_tweets}</body>'
    tail = '</html>'
    html = head + body + tail
    with open(f'var/htmls/{date}.html', 'w') as fp:
        fp.write(html)
