# Togetter Backlogs
Togetterのバックログ（時系列順でみれるという）

## 全体設計
<div align="center">
  <img width="100%" src="https://user-images.githubusercontent.com/4949982/45913267-519f3800-be6a-11e8-9a18-2fd867700323.png">
</div>

## コードスニペット(ウェブフレームワーク)
 - https://github.com/GINK03/flask-seed  
 (flaskで同人サイトのテンプレを作ったときのやつ)  
  

## コールドスタート問題
 - 記事の閲覧数がわかならない場合、ログが貯まるまで、あまり正確なレコメンドはできない（できなくていい）
 - 補完的に動くアルゴリズムは必要

## 法的な制約
 - タイトルを参照しているだけで、本体はTogetterなどコンテンツホルダーに直リンクしていて、薄いWrapper的な役割をこのプロダクトは担っています


