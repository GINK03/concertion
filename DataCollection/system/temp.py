import pandas as pd

df = pd.read_csv('local.csv')

df['PARSED_DATE'] = df['PUB_DATE'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d', errors='ignore'))
df = df[pd.notnull(df['PARSED_DATE'])]
df['PARSED_DATE'].apply(lambda x:print(x.strftime('%Y %V')))
