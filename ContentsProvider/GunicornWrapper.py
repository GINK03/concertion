
import schedule
import time
import os
from pathlib import Path
from os import environ as E
TOP_FOLDER = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
HOME = E['HOME']

def job():
    try:
        # stop gunicorn and reboot
        os.system('pkill gunicorn')
        #time.sleep(10)
        os.system(f'gunicorn -w 4 --bind 0.0.0.0:8443 --chdir {HERE}/project wsgi --keyfile {HOME}/.var/privkey.pem --certfile {HOME}/.var/fullchain.pem')
    except Exception as ex:
        print(ex)


def run():
    schedule.every().day.at("04:30").do(job)
    schedule.every().day.at("12:30").do(job)
    schedule.every().day.at("20:30").do(job)

    job()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    run()
