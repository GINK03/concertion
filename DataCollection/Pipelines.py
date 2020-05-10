import psutil
from pathlib import Path
import time
from inspect import currentframe, getframeinfo
import os
from os import environ as E
import datetime

FILE = Path(__file__).name
HERE = Path(__file__).resolve().parent
TOP_DIR = Path(__file__).resolve().parent.parent.parent

try:
    import sys
    sys.path.append(f'{HERE}')
    import TwitterStatsBatch
    import TwitterIFrames
    import YahooJapanSystem
    import GenerateSitemap
    import Signate
    sys.path.append(f'{TOP_DIR}')
    import Utils
except Exception as exc:
    raise Exception(exc)


def release_resource():
    """
    chromeはプロセスがゾンビ化することがあり、
    chrome関連のプロセスをクリーンアップしなければ行けない
    NOTE: proc.hogehoge()で参照したとき、消えていることがあり、その際はhandle
    """
    ret = os.popen('pgrep chrome | xargs kill -9').read()
    #print(ret)
    for proc in list(psutil.process_iter()):
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
            if 'chrome' in pinfo["name"]:
                os.kill(pinfo['pid'], 0)
        except Exception as exc:
            print(f'[{FILE}] exception = {exc}', file=sys.stderr)

    self_pid = os.getpid()
    try:
        """
        自分の子供プロセスもゾンビ化するので、自分自身以外をkillする
        """
        # 変なところで、procがハンドルできなくるなることがあるので、例外に対応する
        children = psutil.Process(self_pid).children(recursive=True)
        for child in children:
            print(f'[{FILE}] try terminate child = {child.pid}, parent = {self_pid}')
            psutil.Process(child.pid).terminate()
    except Exception as exc:
        print(f'[{FILE}] process kill exception, {exc}', file=sys.stderr)




def run_suit():
    try:
        Utils.DeviceMap.run()
        Utils.CleanTmpDir.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
   
    """
    Signateの最近のコンペの状況を把握する
    """
    try:
        Signate.Signate.run()
    except Exception as exc:
        tb_lineno = sys.exc_info()[2].tb_lineno
        print(f'[{FILE}] exc = {exc}, tb_lineno = {tb_lineno}', file=sys.stderr)
    
    """
    流行ったツイート過去N日分を集計して正しくバッグログに反映する
    """
    if datetime.datetime.now().hour in {5, 18} or E.get("TEST_TWITTER_STAT_BATCH"):
        print(f"[{FILE}] start to run TwitterStatsBatch.AllRecentTwitterRanking.run()...")
        TwitterStatsBatch.AllRecentTwitterRanking.run()
    
    """
    最新の流行ったツイートを集計して表示できるようにする
    NOTE : 現在 disableにしている
    """
    if datetime.datetime.now().hour in {0, 1, 23} or E.get("TEST_TWITTER_STAT_BATCH"):
        ...
        # print(f"[{FILE}] start to run TwitterStatsBatch.CountFreq.run(), analytics_favorited_tweets_010_join_pickle_and_split_by_date, analytics_favorited_tweets_020_call_otherlibs...")
        # release_resource()
        #TwitterStatsBatch.CountFreq.run()
        #TwitterStatsBatch.analytics_favorited_tweets_010_join_pickle_and_split_by_date.run()
        #TwitterStatsBatch.analytics_favorited_tweets_020_call_otherlibs.run()
        #TwitterStatsBatch.generate_html_structures.run()
    
    """
    最新の流行ったツイートを集計して表示できるようにする
    """
    try:
        TwitterIFrames.WrapRecentBuzzTweets.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    
    release_resource()
    print(f'[{FILE}] start to fetch data(A001_fetch)')
    start = time.time()
    try:
        YahooJapanSystem.A001_fetch.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'[{FILE}] end to fetch data(A001_fetch), elapsed = {time.time() - start:0.02f}.')
    release_resource()

    print(f'[{FILE}] start to collect comment(C001_collect).')
    start = time.time()
    try:
        YahooJapanSystem.C001_collect_comment.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'[{FILE}] end to collect comment(C001_collect), elapsed = {time.time() - start:0.02f}.')
    release_resource()

    print(f'[{FILE}] start to make stats(D001_make_stats).')
    start = time.time()
    try:
        YahooJapanSystem.D001_make_stats_and_make_csv.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'[{FILE}] end to make stats(D001_make_stats), elapsed = {time.time() - start:0.02f}.')
    release_resource()

    print(f'[{FILE}] start to make sitemap.')
    start = time.time()
    try:
        GenerateSitemap.generate.run()
    except Exception as exc:
        print(f'[{FILE}][{getframeinfo(currentframe()).lineno}] error occured {exc}', file=sys.stderr)
    print(f'[{FILE}] end to make sitemap, elapsed = {time.time() - start:0.02f}.')


def run():
    # GenerateSitemap.generate.run()
    release_resource()
    while True:
        try:
            run_suit()
        except Exception as exc:
            print(f'[{FILE}] exception in run, exc = {exc}', file=sys.stderr)


if __name__ == '__main__':
    run()
