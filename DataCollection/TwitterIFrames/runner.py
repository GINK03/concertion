
from pathlib import Path
import sys
import warnings

FILE = Path(__file__).name
TOP_FOLDER = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
try:
    sys.path.append(f'{TOP_FOLDER}')
    from Web.Structures import TitleUrlDigestScore
    from Web.Structures import YJComment
    from Web import QueryToDict
    from Web import GetDigest
    sys.path.append(f'{HERE}')

    import PutLocaHtml
    import ReflectHtml
except Exception as exc:
    raise Exception(exc)
warnings.simplefilter("ignore")


def run(url):
    url, digest = PutLocaHtml.put_local_html(url)
    print(url, digest)
    fetch_url = ReflectHtml.reflect_html(digest)
    return fetch_url, digest, url

if __name__ == '__main__':
    
    # url = 'https://twitter.com/shinsangenya/status/1229185306051506176'
    url = sys.argv[1]
    fetch_url, diget, url = run(url)
    print(fetch_url, diget, url)
