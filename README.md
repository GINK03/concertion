# ai_news
gunosyのようなレコメンド系のニュースサイト

## 全体設計
<div align="center">
  <img width="100%" src="https://user-images.githubusercontent.com/4949982/45913267-519f3800-be6a-11e8-9a18-2fd867700323.png">
</div>

## コードスニペット(スクレイピング)
 - https://github.com/GINK03/scraping-designs  
 (スクレイピングのいろいろなデザイン)
 
## コードスニペット(ウェブフレームワーク)
 - https://github.com/GINK03/flask-seed  
 (flaskで同人サイトのテンプレを作ったときのやつ)  
  
## 機械学習アルゴリズム
 - https://github.com/GINK03/k8s-lgb-score-check

## コールドスタート問題
 - 記事の閲覧数がわかならない場合、ログが貯まるまで、あまり正確なレコメンドはできない（できなくていい）
 - 補完的に動くアルゴリズムは必要

## 法的な制約
 - [SmartNewsは違法アプリ？　ニュースアプリの仕様と著作権の関係](https://www.excite.co.jp/News/android/20130616/Androidsmart_65504.html)


## controler(予想機)のサンプルアウトプット
```console
https://gunosy.com/articles/a6qEb 66.92806005763008
https://gunosy.com/articles/aDG0Q 75.71861594115387
https://gunosy.com/articles/aXpLA 58.4426293922232
https://gunosy.com/articles/RmWEb 58.26595935523244
https://gunosy.com/articles/RQNmh 71.16854449814142
https://gunosy.com/articles/aZ4GA 54.36219616365624
https://gunosy.com/articles/RSFIj 53.555376021738155
https://gunosy.com/articles/RoJql 67.02434120013594
https://gunosy.com/articles/RpTM4 48.65043252331669
https://gunosy.com/articles/RmvzF 89.8151063084708
http://vippers.jp/archives/9197075.html 74.4024379780589
http://vippers.jp/archives/9196655.html 54.44861920282121
http://vippers.jp/archives/9197075.html 74.4024379780589
http://vippers.jp/archives/9196655.html 54.44861920282121
http://vippers.jp/archives/9195755.html 61.50695391535349
http://vippers.jp/archives/9198359.html 92.5907185980916
http://vippers.jp/archives/9196552.html 93.48324135571687
http://vippers.jp/archives/9198453.html 50.412734637931194
http://vippers.jp/archives/9196552.html 93.48324135571687
http://vippers.jp/archives/9197435.html 78.63533977477054
http://vippers.jp/archives/9194902.html 63.383173869571536
http://vippers.jp/archives/9194570.html 89.78290128878511
```
