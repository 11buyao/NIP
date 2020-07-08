# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : search_indexes.py
# Author: TheWu
# Date  : 2020/3/22

"""

"""
from haystack import indexes

from .models import News


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    """
    索引模型类
    """
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    clicks = indexes.IntegerField(model_attr='clicks')
    image_url = indexes.CharField(model_attr='image_url')
    update_time = indexes.DateTimeField(model_attr='update_time')

    def get_model(self):
        """返回建立索引的模型类
        """
        return News

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集
        """

        return self.get_model().objects.filter(is_delete=False)
