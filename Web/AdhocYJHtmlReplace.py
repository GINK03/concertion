import gzip
from typing import List
from bs4 import BeautifulSoup
import sys
from pathlib import Path
import glob
import pickle
import json
import re
import requests

FILE = Path(__file__).name
TOP_DIR = Path(__file__).resolve().parent.parent
HOME = Path.home()
try:
    sys.path.append(f'{TOP_DIR}')
    from Web.Structures import YJComment
    from Web import GetDigest
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


from urllib.parse import urlparse
def get_nexts(href: str, next_paragraphs: List[BeautifulSoup]) -> None:
    try:
        digest = GetDigest.get_digest(href)
        Path(f"{TOP_DIR}/var/YJ/NextPages/").mkdir(exist_ok=True, parents=True)
        if Path(f'{TOP_DIR}/var/YJ/NextPages/{digest}').exists():
            # load
            with open(f'{TOP_DIR}/var/YJ/NextPages/{digest}', 'rb') as fp:
                html = gzip.decompress(fp.read()).decode("utf8")
        else:
            o = urlparse(href)._replace(scheme="https", netloc="news.yahoo.co.jp")
            with requests.get(o.geturl()) as r:
                html = r.text
            # save
            with open(f'{TOP_DIR}/var/YJ/NextPages/{digest}', 'wb') as fp:
                fp.write(gzip.compress(bytes(html, "utf8")))
        next_soup = BeautifulSoup(html, "html5lib")
        next_paragraph = next_soup.find(attrs={"class": "paragraph"})
        if next_paragraph is None:
            next_paragraph = next_soup.find(attrs={"id": "uamods"})

        next_page_li = next_soup.find("li", attrs={"class": "next"})
        if next_page_li is None:
            next_page_li = next_soup.find("li", attrs={"class": "pagination_item-next"})
        for section in next_paragraph.find_all("section"):
            if "【関連記事】" in section.__str__():
                section.decompose()
        next_paragraphs.append(next_paragraph)
        if next_page_li and next_page_li.find("a"):
            get_nexts(href=next_page_li.find("a").get("href"), next_paragraphs=next_paragraphs)
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)

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
        """ 2020/06/09追加 """
        if soup.find(attrs={"id":"msthd"}):
            soup.find(attrs={"id":"msthd"}).decompose()
        if soup.find(attrs={"id":"yjnHeader_nav"}):
            soup.find(attrs={"id":"yjnHeader_nav"}).decompose()
        if soup.find(attrs={"id":"uamods-also_read"}):
            soup.find(attrs={"id":"uamods-also_read"}).decompose()
        if soup.find(attrs={"id":"newsFeed"}):
            soup.find(attrs={"id":"newsFeed"}).decompose()
        if soup.find(attrs={"id":"yjSLink"}):
            soup.find(attrs={"id":"yjSLink"}).decompose()
        """ sectionの中に’関連記事’の文字列が含まれていたら削除 """
        for section in soup.find_all("section"):
            if "【関連記事】" in section.__str__():
                section.decompose()
        """ comment disable button """
        if soup.find(attrs={"class":"checkbox"}):
            soup.find(attrs={"class":"checkbox"}).decompose()
        """ 2020/06 古い削除ルールセット """   
        for key, value in [("class", "listPaneltype"), 
                            ("class", "mainYdn"), 
                            ("id", "timeline"), 
                            ("id", "yjSLink"), 
                            ("class", "ynDetailRelArticle"), 
                            ("class", "commentBox"),
                            ("id", "contentsFooter"),
                            ("id", "footer"),
                            ("id", "stream_title"), 
                            ("id", "contentsHeader"), 
                            ("id", "yjnFooter")]:
            if soup.find(attrs={key:value}):
                soup.find(attrs={key: value}).decompose()

        """ 画像の説明のhrefを消す """
        if soup.find(attrs={"class": "photoOffer"}):
            del soup.find(attrs={"class": "photoOffer"}).find("a")["href"]
        """ contents中のリンクを削除 """
        for key, value in [("id", "uamods"), ("id", "paragraph")]:
            paragraph = soup.find(attrs={key: value})
            if paragraph is None:
                continue
            for a in paragraph.find_all("a"):
                # if a.get("href"):
                #    del a["href"]
                """ a -> spanに変更 """
                a.name = "span"
        """ テキストリンクの装飾を消す """
        for a in soup.find_all(attrs={"class": "yjDirectSLinkHl"}):
            del a["class"]
        """ fontをWeb Fontの明朝に変更"""
        soup.find("head").insert(-1, BeautifulSoup('<link href="https://fonts.googleapis.com/css?family=Noto+Serif+JP:400,700&display=swap&subset=japanese" rel="stylesheet">', 'lxml'))
        soup.find("body")["style"] = "font-family: 'Noto Serif JP' !important;"

        """ javascriptによるクリック発火を抑制 """
        for a in soup.find_all("a", {"onmousedown": True}):
            del a["onmousedown"]

        """ stylesheetの一部を削除 """
        # soup.find(attrs={"href": "https://s.yimg.jp/images/jpnews/cre/article/pc/css/article_pc_v7.0.css"}).decompose()

        """ 次のページをパースして統合 """
        next_page_li = soup.find("li", attrs={"class": "next"})
        if next_page_li is None:
            next_page_li = soup.find("li", attrs={"class": "pagination_item pagination_item-next"})
        if next_page_li and next_page_li.find("span"):
            next_paragraphs: List[BeautifulSoup] = []
            get_nexts(next_page_li.find("span").get("href"), next_paragraphs)
            print("total page size", len(next_paragraphs))
            for idx, next_paragraph in enumerate(next_paragraphs):
                if soup.find(attrs={"class": "articleMain"}):
                    soup.find(attrs={"class": "articleMain"}).insert(-1, next_paragraph)
                    soup.find(attrs={"class": "articleMain"}).insert(-1, BeautifulSoup(f"""<p align="center"> Page {idx+2} </p>""", "lxml"))

                elif soup.find(attrs={"id": "uamods"}):
                    soup.find(attrs={"id": "uamods"}).insert(-1, next_paragraph)
                    soup.find(attrs={"id": "uamods"}).insert(-1, BeautifulSoup(f"""<p align="center"> Page {idx+2} </p>""", "lxml"))
                # print(next_paragraph)

            """ pageを示すフッターを消す """
            # soup.find(attrs={"class": "marT10"}).decompose()
            # soup.find(attrs={"class": "fdFt"}).decompose()
            """ page送りを消す """
            if soup.find(attrs={"class": "pagination_items"}):
                for pagination_item in soup.find_all(attrs={"class": "pagination_items"}):
                    pagination_item.decompose()
            """ footerを最後以外のものを消す """
            footers = soup.find_all("footer")
            if footers.__len__() >= 2:
                for footer in footers[:-1]:
                    footer.decompose()
            """ 次ページは：の文字を消す """
            for a in soup.find_all("a", attrs={"class": re.compile("sc-.*?")}):
                if "次ページは：" in a.__str__():
                    a.decompose()
            """ remove headers without head """
            for header in soup.find_all("header")[2:]:
                header.decompose()
        """ もとURLを挿入 """
        original_url = soup.find("meta", attrs={"property": "og:url"}).get("content")
        if soup.find(attrs={"class": "contentsWrap"}):
            soup.find(attrs={"class": "contentsWrap"}).insert(-1, BeautifulSoup(f"""<a href="{original_url}"><p align="center">オリジナルURL</p></a>""", "lxml"))
        # paragraph.find("a", {"class":None, "href":True}).decompose()
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f'[{FILE}] decompose error, exc = {exc}, tb_lineno = {tb_lineno}', file=sys.stderr)

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
        # print(soup)
        if soup.find("div", {"id":"sub"}) is not None:
            target_id = "sub"
        else:
            target_id = "yjnSub"
        with open(f"{HOME}/tmp", "w") as fp:
            fp.write(soup.__str__())
        soup.find('div', {'id': target_id}).string = ''
        soup.find('div', {'id': target_id}).insert(1, BeautifulSoup(comment_html, 'html5lib'))
        
        if soup.find(attrs={"id": "contentsWrap"}):
            target_id = "contentsWrap"
        else:
            target_id = "main"
        soup.find('div', {'id': target_id}).append(BeautifulSoup(get_form_html(digest), 'html5lib'))
        soup.find('div', {'id': target_id}).append(BeautifulSoup(this_site_comments, 'html5lib'))
        soup.find('div', {'id': target_id}).append(BeautifulSoup(comment_html_below, 'html5lib'))
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f'[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}', file=sys.stderr)
        return f"[{FILE}] Cannnot handle this page, exc = {exc}, tb_lineno = {tb_lineno}"
    return str(soup)
