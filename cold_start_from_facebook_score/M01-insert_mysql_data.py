import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()

class HTML(Base):
		__tablename__ = 'html'
		url		= sa.Column(sa.String, primary_key=True)
		score = sa.Column(sa.FLOAT)
		title = sa.Column(sa.BLOB)
		body	= sa.Column(sa.BLOB)
		 
url = 'mysql+pymysql://root:mysql@localhost/mydatabase?charset=utf8'
engine = sa.create_engine(url, echo=True)
Session = sa.orm.sessionmaker(bind=engine)
session = Session()

session.query(HTML).delete()

from pathlib import Path
import json
from datetime import *
import json
import time
import schedule
from hashlib import sha256
from bs4 import BeautifulSoup as BS
import gzip
def job():
	now = datetime.now()
	url_score = {}
	for path in Path('./facebook_score_v2').glob('*'):
		obj = json.load(path.open())		
		parsed_dates = []
		for key, val in obj.items():
						if key == 'url':
										continue
						parsed_date = datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
						parsed_dates.append(parsed_date)
		min_date_delta = min([now - parsed_date for parsed_date in parsed_dates])
		# 48時間以上古いものはスキップ
		if min_date_delta.days >= 2:
						continue
		#print(key,val, parsed_date)
		#print(min_date_delta)
		# 最大の時間を取り出し, そのfbの結果をみる
		max_date = max(parsed_dates)
		engagement = obj[max_date.strftime('%Y-%m-%d %H:%M:%S')]['engagement']
		reaction_count = engagement['reaction_count']
		url = obj['url']
		url_score[url] = reaction_count

	url_score = [(url,score) for url,score in url_score.items()]
	url_score = sorted(url_score, key=lambda x:x[1]*-1)[:100]

	url_score = {url:score for url, score in url_score}

	# urlのtitle descをパース
	for url, score in url_score.items():
		hashed = sha256(bytes(url,'utf8')).hexdigest()
		if Path(f'./htmls/{hashed}.gz').exists() is False:
			continue
		print('ok')
		try:
			soup = BS(gzip.decompress(open(f'./htmls/{hashed}.gz', 'rb').read()).decode())
			h1 = soup.find('div', {'class':'hd'}).find('h1').text.strip()
			paragraph = soup.find('div', {'class':'paragraph'}).text.strip()
			#print(paragraph)
			url, score, title, body = bytes(url,'utf8'), float(score), bytes(h1,'utf8'), bytes(paragraph,'utf8')
			ret = session.query(HTML.url).filter_by(url=url).scalar()
			if ret is None:	
				session.add( HTML(url=url, score=score, title=title, body=body) )
				session.commit()
		except Exception as ex:
			print(ex)
			continue
	#ser = json.dumps(url_datum, indent=2, ensure_ascii=False)
	#open('pre_calculated_jsons/default_facebook_datum.json', 'w').write(ser)
job()
schedule.every(10).minutes.do(job)
while True:
				schedule.run_pending()
				time.sleep(1)
