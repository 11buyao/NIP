# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : urls.py
# Author: TheWu
# Date  : 2020/2/27

"""

"""
from . import views
from django.urls import path

app_name = 'news'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:news_id>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('news/banners/', views.BannerView.as_view(), name='banners'),
    path('news/comments/thumbsup/', views.ThumbsUpView.as_view(), name='thumbs_up'),
    path('news/<int:news_id>/comments/', views.CommentsView.as_view(), name='comments'),
    path('search/', views.SearchView(), name='search'),
    path('voice/', views.WordToVoiceView.as_view(), name='voice'),
]
