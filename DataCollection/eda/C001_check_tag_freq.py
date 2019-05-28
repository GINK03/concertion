import pandas as pd
import json
df = pd.read_csv('local.csv')

def json_parse(x):
    try:
        return json.loads(x)
    except:
        return None
tag_freq = {}
for tags in df['TAGS'].apply(json_parse):
    if tags is None:
        continue
    for tag in tags:
        if tag_freq.get(tag) is None:
            tag_freq[tag] = 0
        tag_freq[tag] += 1

dfR = pd.DataFrame([{'TAG':tag, 'FREQ':freq} for tag, freq in tag_freq.items()])

dfR = dfR.sort_values(by=['FREQ'])
dfR.to_csv('tag_freq.csv', index=None)
