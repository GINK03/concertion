
import schedule
import time
import A001_collection
import B001_sql_to_csv
import C001_check_tag_freq

def job():
    #print("I'm working...")
    try:
        A001_collection.run()
        B001_sql_to_csv.run()
        C001_check_tag_freq.run()
    except Exception as ex:
        print(ex)

schedule.every().hour.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
