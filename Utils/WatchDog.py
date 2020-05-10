
"""
Lineに対して何会場があった場合に自分に送ることで
できるだけ早く異常を検知する
NOTE: token自体は自分に送信しか出来ないので別にバレても良い
"""

import schedule
import json
import requests
import time


TOKEN = "uy19NzDMlHTdmMFr54lnDoKZXWQhEv0D9bRaSXqsICF"
URL = "https://notify-api.line.me/api/notify"


def send_to_line(message: str) -> None:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN
    }
    data = {"message": f"{message}"}
    ret = requests.post(URL, params=data, headers=headers)


def watch_dog():
    try:
        with requests.get("https://concertion.page", timeout=60) as r:
            if r.status_code != 200:
                raise Exception(f"status_code error = {r.status_code}")
    except Exception as exc:
        send_to_line(str(exc))

watch_dog()

while True:
    schedule.every(10).minutes.do(watch_dog)
    time.sleep(1)
    

