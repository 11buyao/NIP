# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : urls.py
# Author: TheWu
# Date  : 2020/3/1

"""

"""
from . import views
from django.urls import path, re_path

app_name = 'verifications'
urlpatterns = [
    path('image_code/<uuid:image_code_id>/', views.ImageCodeView.as_view(), name='image_code'),
    re_path('username/(?P<username>[\w_\u4e00-\u9fa5]{2,20})/', views.CheckUsernameView.as_view(),
            name='check_username'),
    re_path('mobile/(?P<mobile>1[345789]\d{9})/', views.CheckMobileView.as_view(), name='check_mobile'),
    path('sms_code/', views.SmsCodeView.as_view(), name='sms_code'),
]
