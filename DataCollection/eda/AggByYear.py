import pandas as pd

df = pd.read_csv('local.csv')
def filter_no_time(x):
    x = str(x)
    if len(x.split('-')) == 3:
        return True
    else:
        return False

df = df[df['PUB_DATE'].apply(filter_no_time)]
df['YEAR'] = df['PUB_DATE'].apply(lambda x:str(x).split('-')[0])
df['MONTH'] = df['PUB_DATE'].apply(lambda x:str(x).split('-')[1])
df['YEAR_MONTH'] = df['PUB_DATE'].apply(lambda x:'-'.join(str(x).split('-')[0:2]))
df['YEAR_MONTH_DAY'] = df['PUB_DATE'].apply(lambda x:'-'.join(str(x).split('-')[0:3]))
for YEAR_MONTH, subDf in df.groupby(by=['YEAR_MONTH']):
    print(YEAR_MONTH) #, subDf.sort_values(by=['ICON_VIEW'], ascending=False).head())
