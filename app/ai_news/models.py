import os

from django.db import models


class Article(models.Model):

    # id = models.IntegerField()
    # URL
    url = models.URLField()
    # score
    score = models.IntegerField()
    # ヘッダー
    h1 = models.TextField()
    # 本文
    paragraph = models.TextField()
    # path
    # img_path = models.FilePathField(os.path.dirname(os.path.abspath(__file__)))
