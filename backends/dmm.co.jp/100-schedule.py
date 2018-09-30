
import schedule
import os
def job():
	os.system('python3 00-scrape.py')
	os.system('python3 10-parse-fill.py') 

schedule.every(60).minutes.do(job)
#schedule.every(1).minutes.do(job)
job()
while True:
  schedule.run_pending()
  time.sleep(1)
