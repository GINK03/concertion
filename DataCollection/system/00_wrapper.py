
import schedule
import time
from pathlib import Path
from datetime import datetime
import sys
try:
    HERE = Path(__file__).resolve().parent
    sys.path.append(f'{HERE}')
    import A001_collection
    import B001_convert_data_to_csv
    import C001_check_tag_freq
except Exception as exc:
    raise Exception(exc)

def job():
    #print("I'm working...")
    try:
        A001_collection.run()
        B001_convert_data_to_csv.run()
        C001_check_tag_freq.run()
        print('last', datetime.now()) 
    except Exception as ex:
        print(ex)

#schedule.every().hour.do(job)
schedule.every().day.at("00:30").do(job)
schedule.every().day.at("08:30").do(job)
schedule.every().day.at("16:30").do(job)

job()
while True:
    schedule.run_pending()
    time.sleep(1)
