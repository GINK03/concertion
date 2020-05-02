from bs4 import BeautifulSoup
import glob
import sys
from pathlib import Path

TOP_DIR = Path(__file__).resolve().parent.parent
FILE = Path(__file__).name
def get_buzz_tweet() -> str:
    """
    1. 最新のtweetの取得リストから, 最新の取得したツイート(aka. 最後尾のツイート)を取得する
    2. 最終加工後のdivがNoneになることがあり、ハンドリングする
    3. 正常に処理できたツイートがN件に達したら打ち切り
    Args:
        - nothing
    Returns:
        - str: 最新のバズったツイート
    """
    dir_fn = sorted(glob.glob(f'{TOP_DIR}/var/Twitter/tweet/*'))[-1]
    buzzes = []
    count = 0
    for idx, fn in enumerate(glob.glob(f'{dir_fn}/*')[-100:]):
        try:
            html = open(fn).read()
            soup = BeautifulSoup(html, features='lxml')
            div = soup.find('body').find('div')
            if div.find(attrs={'class': 'EmbeddedTweet'}):
                div.find(attrs={'class': 'EmbeddedTweet'})['style'] = 'margin-top: 10px; margin-left: 10px;'
            imagegrids = soup.find_all('a', {'class': 'ImageGrid-image'})
            for imagegrid in imagegrids:
                src = imagegrid.find('img').get('src')
                imagegrid['href'] = src
            mediaassets = soup.find_all('a', {'class': 'MediaCard-mediaAsset'})
            for mediaasset in mediaassets:
                if mediaasset.find('img') and mediaasset.find('img').get('alt') != 'Embedded video':
                    mediaasset['href'] = mediaasset.find('img').get('src')
            """
            NOTE: このツイートについて評論するを追加
            soup.insert(-1, left_soup)はsoupの最後に要素を追加するということ
            """
            append_soup = BeautifulSoup(div.find(attrs={"class":"CallToAction"}).__str__(), "lxml")
            try:
                append_soup.find(attrs={"class":"CallToAction-text"}).string = "評論する"
            except Exception as exc:
                print(exc)
            day_name = Path(fn).parent.name
            tweet_digest = Path(fn).name
            for a in append_soup.find_all("a", {"href": True}):
                a["href"] = f"/TweetHyoron/{day_name}/{tweet_digest}"
            div.find(attrs={"class":"EmbeddedTweet-tweetContainer"}).insert(-1, append_soup)

            """
            NOTE: divがNoneならばスキップする
            """
            if div is None:
                continue
            buzz_ctx = div.__str__()
            """
            NOTE: stypleが見つからなかったら空白で代替
            """
            buzz_css = soup.find('body').find('style').__str__() if soup.find('body').find('style') else ""
            buzzes.append(buzz_ctx + buzz_css)
            count += 1

            if count >= 10:
                break
        except Exception as exc:
            tb_lineno = sys.exc_info()[2].tb_lineno
            print(f"[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}", file=sys.stderr)
    html = '\n'.join(buzzes)
    return html
