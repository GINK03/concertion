import glob
from pathlib import Path
import sys
FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent

try:
    import sys
    sys.path.append(f'{TOP_DIR}')
    from Web import Hostname
except Exception as exc:
    print(f'[{__file__}] {exc}', file=sys.stderr)
    raise Exception(exc)


def generate_daily_ranking_list() -> str:
    inner = ''
    for fn in reversed(sorted(glob.glob(f'{TOP_DIR}/var/YJ/ranking_stats_daily/*.csv'))): 
        name = Path(fn).name.replace('.csv', '')
        tmp = f'<a href="https://{Hostname.hostname()}/daily_yj_abstracts/{name}">{name}</a><br>'
        inner += tmp
    return inner
