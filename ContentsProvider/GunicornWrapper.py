
import schedule
import time
import os
from pathlib import Path
import datetime
from os import environ as E
TOP_FOLDER = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
HOME = E['HOME']

def job():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    Path(f'{TOP_FOLDER}/var/log').mkdir(exist_ok=True, parents=True)
    try:
        # stop gunicorn and reboot
        # os.system('pkill gunicorn')
        #time.sleep(10)
        os.system(f'gunicorn -w 4' \
                    f' --bind 0.0.0.0:443' \
                    f' --chdir {HERE}/project wsgi' \
                    f' --keyfile {HOME}/.var/privkey.pem' \
                    f' --certfile {HOME}/.var/fullchain.pem' \
                    f' --access-logfile {TOP_FOLDER}/var/log/access_{now}.log' \
                    f' --error-logfile {TOP_FOLDER}/var/log/error_{now}.log'
                    )
    except Exception as exc:
        print(exc)


def run():
    # schedule.every().day.at("04:30").do(job)
    # schedule.every().day.at("12:30").do(job)
    # schedule.every().day.at("20:30").do(job)
    # while True:
    #    schedule.run_pending()
    #    time.sleep(1)
    while True:
        job()

if __name__ == '__main__':
    run()
