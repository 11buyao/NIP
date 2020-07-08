# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : urls.py
# Author: TheWu
# Date  : 2020/3/28

"""

"""
from django.urls import path
from . import views

app_name = 'admin'

urlpatterns = [
    path('admin/', views.IndexView.as_view(), name='index'),
    path('admin/tag/', views.TagManageView.as_view(), name='tag'),
    path('admin/tag/<int:tag_id>/', views.TagManageView.as_view(), name='tag_edit'),
    path('admin/tag/<int:tag_id>/news/', views.NewsByTagView.as_view(), name='news_by_tag'),

    path('admin/news/', views.NewsManageView.as_view(), name='news'),
    path('admin/news/<int:news_id>/', views.NewsEditView.as_view(), name='news_edit'),
    path('admin/news/pub/', views.NewsPubView.as_view(), name='news_pub'),

    path('admin/banner/', views.BannerManageView.as_view(), name='banner'),
    path('admin/banner/<int:banner_id>/', views.BannerManageView.as_view(), name='banner_edit'),
    path('admin/banner/add/', views.BannerAddView.as_view(), name='banner_add'),

    path('admin/group/', views.GroupManageView.as_view(), name='group'),
    path('admin/group/<int:g_id>/', views.GroupEditView.as_view(), name='group_edit'),
    path('admin/group/add/', views.GroupAddView.as_view(), name='group_add'),

    path('admin/users/', views.UserManageView.as_view(), name='users'),
    path('admin/users/<int:user_id>/', views.UserEditView.as_view(), name='user_edit'),

    path('admin/upload/', views.UpToServerView.as_view(), name='up_to_server'),
    path('markdown/', views.MarkdownUploadView.as_view(), name='markdown_image_upload'),

]
