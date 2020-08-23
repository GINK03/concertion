
from pathlib import Path
import os

HERE = Path(__file__).resolve().parent

HOME = Path.home().__str__()

run_cmd_web = f"gunicorn -w 16 --bind 0.0.0.0:443 --chdir {HERE}/project wsgi --keyfile /etc/letsencrypt/live/concertion.page/privkey.pem --certfile /etc/letsencrypt/live/concertion.page/fullchain.pem"
run_cmd_local = f"gunicorn -w 16 --bind 0.0.0.0:80 --chdir {HERE}/project wsgi"

for i in range(10):
    os.system(run_cmd_web)
