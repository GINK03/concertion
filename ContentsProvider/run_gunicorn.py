
from pathlib import Path
import os

HERE = Path(__file__).resolve().parent

HOME = Path.home().__str__()
mount_dir = f"{HOME}/ikazuchi"

run_cmd = f"gunicorn -w 16 --bind 0.0.0.0:443 --chdir {HERE}/project wsgi --keyfile /etc/letsencrypt/live/concertion.page/privkey.pem --certfile /etc/letsencrypt/live/concertion.page/fullchain.pem"
unmount_cmd = f"fusermount -zu {mount_dir}"
remount_cmd = f"sshfs gimpei@192.168.40.16:{HOME} {mount_dir} -o nonempty,allow_other,reconnect,identityfile=/home/gimpei/.ssh/id_github"

for i in range(10):
    os.system(run_cmd)
    os.sysmte(unmound_cmd)
    os.system(remount_cmd)
