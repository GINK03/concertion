from bs4 import BeautifulSoup
import sys
from pathlib import Path
import glob
import pickle
import json

FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent
try:
    sys.path.append(f'{TOP_DIR}')
    from Web.Structures import YJComment
except Exception as exc:
    raise Exception(exc)


def get_form_html(digest):
    html = f"""
    <form action="/blobs_yj/{digest}" class="form" method="post">
        <textarea value="コメント" name="YJComment" cols="55" rows="5" id="YJComment" style="-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;-webkit-background-clip: padding;-moz-background-clip: padding;background-clip: padding-box;-webkit-border-radius: 0;-moz-border-radius: 0;-ms-border-radius: 0;-o-border-radius: 0;border-radius: 0;-webkit-appearance: none;background-color: white;border: 1px solid;border-color: #848484 #c1c1c1 #e1e1e1;color: black;outline: 0;margin: 0;padding: 2px 3px;text-align: left;font-size: 13px;font-family: Arial, &quot;Liberation Sans&quot;, FreeSans, sans-serif;height: auto;vertical-align: top;min-height: 40px;overflow: auto;resize: vertical;width: 100%" ></textarea>
        <input type="submit" name="YJSubmit" value="Submit" style="-webkit-appearance: none;-webkit-border-radius: 4px;-moz-border-radius: 4px;-ms-border-radius: 4px;-o-border-radius: 4px;border-radius: 4px;-webkit-background-clip: padding;-moz-background-clip: padding;background-clip: padding-box;background: #ddd url(../images/button.png?1298351022) repeat-x;background-image: linear-gradient(#fff, #ddd);border: 1px solid;border-color: #ddd #bbb #999;cursor: pointer;color: #333;display: inline-block;font: bold 12px/1.3 &quot;Helvetica Neue&quot;, Arial, &quot;Liberation Sans&quot;, FreeSans, sans-serif;outline: 0;overflow: visible;margin: 0;padding: 3px 10px;text-shadow: white 0 1px 1px;text-decoration: none;vertical-align: top;width: auto">
    </from>
    """
    return html


def yj_html_replace(html: str, digest: str) -> str:
    """
    必要なフォーマットに変換して、htmlを返却
    """
    soup = BeautifulSoup(html, 'html5lib')
    try:
        for a in soup.find('head').find_all('script'):
            a.decompose()
        for a in soup.find('body').find_all('script'):
            a.decompose()
        for a in soup.find_all('iframe'):
            a.decompose()
        soup.find(attrs={'class': 'listPaneltype'}).decompose()
        soup.find(attrs={'class': 'mainYdn'}).decompose()
        soup.find(attrs={'id': 'timeline'}).decompose()
        soup.find(attrs={'id': 'yjSLink'}).decompose()
        if soup.find(attrs={'class': 'ynDetailRelArticle'}) is not None:
            soup.find(attrs={'class': 'ynDetailRelArticle'}).decompose()
        if soup.find(attrs={'class': 'commentBox'}) is not None:
            soup.find(attrs={'class': 'commentBox'}).decompose()

        soup.find(attrs={'id': 'contentsFooter'}).decompose()
        soup.find(attrs={'id': 'footer'}).decompose()
        soup.find(attrs={'class': 'stream_title'}).decompose()
        soup.find(attrs={'id': 'contentsHeader'}).decompose()
        """ 画像の説明のhrefを消す """
        if soup.find(attrs={"class":"photoOffer"}):
            del soup.find(attrs={"class":"photoOffer"}).find("a")["href"]
        """ パラグラフ中のリンクを削除 """
        paragraph = soup.find(attrs={"class":"paragraph"})
        for a in paragraph.find_all("a"):
            if a.get("href"):
                del a["href"]
        #paragraph.find("a", {"class":None, "href":True}).decompose()
    except Exception as exc:
        print(f'[{FILE}] decompose error, {exc}', file=sys.stderr)

    print(f'[{FILE}] accessing to {TOP_DIR}/var/YJ/comments/{digest}', file=sys.stdout)
    comment_html = ''
    comment_html_below = ''
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
                tb_lineno = sys.exc_info()[2].tb_lineno
                print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)
                Path(fn).unlink()
                comments = []
        for comment in list(reversed(sorted(comments, key=lambda x: x.ts)))[:20]:
            tmp = f'''<div class="comment">
                        <div class="username">😃{comment.username}</div>
                        <div class="text">{comment.comment}</div>
                        <div class="ts-view" style="font-size:xx-small;text-align:right;">{comment.ts}</div>
                        <div class="good-bad">👍x{comment.good} 👎x{comment.bad}</div>
                    </div><br>'''
            comment_html += tmp

        for comment in list(reversed(sorted(comments, key=lambda x: x.ts)))[20:]:
            tmp = f'''<div class="comment">
                        <div class="username">😃{comment.username}</div>
                        <div class="text">{comment.comment}</div>
                        <div class="ts-view" style="font-size:xx-small;text-align:right;">{comment.ts}</div>
                        <div class="good-bad">👍x{comment.good} 👎x{comment.bad}</div>
                    </div><br>'''
            comment_html_below += tmp
    """
    1. ログインしたユーザのコメント等も乗せる
    2. コメント欄も表示
    3. {TOP_DIR}/var/YJ/YJComment/{digest} に時系列の名前で、json形式で入っている
    """
    this_site_comments = ""
    for fn in reversed(sorted(glob.glob(f"{TOP_DIR}/var/YJ/YJComment/{digest}/*"))):
        obj = json.load(open(fn))
        tmp = f'''<div class="comment">
                    <div class="username">😃{obj["screen_name"]}</div>
                    <div class="text">{obj["YJComment"]}</div>
                    <div class="ts-view" style="font-size:xx-small;text-align:right;">{obj["datetime"]}</div>
                    <div class="good-bad">👍x{0} 👎x{0}</div>
                </div><br>'''
        this_site_comments += tmp

    try:
        soup.find('div', {'id': 'sub'}).string = ''
        soup.find('div', {'id': 'sub'}).insert(1, BeautifulSoup(comment_html, 'html5lib'))
        soup.find('div', {'id': 'main'}).append(BeautifulSoup(get_form_html(digest), 'html5lib'))
        soup.find('div', {'id': 'main'}).append(BeautifulSoup(this_site_comments, 'html5lib'))
        soup.find('div', {'id': 'main'}).append(BeautifulSoup(comment_html_below, 'html5lib'))
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f'[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}', file=sys.stderr)
        return "Cannnot handle this page"
    return str(soup)
