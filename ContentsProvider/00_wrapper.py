
import schedule
import time
import os
'''
rootで動作されることを期待している
'''
def job():
    try:
        # stop gunicorn and reboot
        os.system('pkill gunicorn')    
        time.sleep(10)
        os.system('sh run_gunicorn.sh')
    except Exception as ex:
        print(ex)

schedule.every().day.at("04:30").do(job)
schedule.every().day.at("12:30").do(job)
schedule.every().day.at("20:30").do(job)

job()
while True:
    schedule.run_pending()
    time.sleep(1)
