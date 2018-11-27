from django.shortcuts import render


# webpackが生成したhtmlをそのままテンプレートとして読み込ませる
def index(request):
    return render(request, 'index.html', {})
