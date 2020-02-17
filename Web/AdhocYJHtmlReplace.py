
from bs4 import BeautifulSoup
import sys
from pathlib import Path
import glob
import pickle
FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f'{TOP_DIR}')
    from Web.Structures import YJComment
except Exception as exc:
    raise Exception(exc)
def yj_html_replace(html:str, digest:str) -> str:
    soup = BeautifulSoup(html, 'html5lib')

    for a in soup.find('head').find_all('script'):
        a.decompose()
    soup.find(attrs={'class':'listPaneltype'}).decompose()
    soup.find(attrs={'class':'mainYdn'}).decompose()
    soup.find(attrs={'id':'timeline'}).decompose()
    soup.find(attrs={'id':'yjSLink'}).decompose()
    if soup.find(attrs={'class':'ynDetailRelArticle'}) is not None:
        soup.find(attrs={'class':'ynDetailRelArticle'}).decompose()
    if soup.find(attrs={'class':'commentBox'}) is not None:
        soup.find(attrs={'class':'commentBox'}).decompose()

    soup.find(attrs={'id':'contentsFooter'}).decompose()
    soup.find(attrs={'id':'footer'}).decompose()
    soup.find(attrs={'class':'stream_title'}).decompose()
    soup.find(attrs={'id':'contentsHeader'}).decompose()
    print(f'{TOP_DIR}/var/YJ/comments/{digest}/*')
    comment_html = ''
    fns = sorted(glob.glob(f'{TOP_DIR}/var/YJ/comments/{digest}/*.pkl'))
    if len(fns) == 0:
        comment_html = '誰もコメントしていません'
    else:
        # last is lastest comment
        fn = fns[-1]
        with open(fn, 'rb') as fp:
            try:
                comments: YJComment = pickle.load(fp)
            except EOFError as exc:
                print(exc)
                Path(fn).unlink()
                comments = []
        for comment in list(reversed(sorted(comments, key=lambda x:x.ts)))[:20]:
            tmp = f'''<div class="comment">
                        <div class="username">😃{comment.username}</div>
                        <div class="text">{comment.comment}</div>
                        <div class="ts-view" style="font-size:xx-small;text-align:right;">{comment.ts}</div>
                        <div class="good-bad">👍x{comment.good} 👎x{comment.bad}</div>
                    </div><br>'''
            comment_html += tmp 

    soup.find('div', {'id':'sub'}).string = ''
    soup.find('div', {'id':'sub'}).insert(1, BeautifulSoup(comment_html, 'html5lib')) #.replace_with(str(comments))
    return str(soup)
