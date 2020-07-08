# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : urls.py
# Author: TheWu
# Date  : 2020/2/27

"""

"""
from . import views
from django.urls import path

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('find_pwd/', views.FindPasswordView.as_view(), name='find_pwd'),
    path('change_pwd/', views.ChangePasswordView.as_view(), name='change_pwd'),
    path('fit/', views.UserManageView.as_view(), name='user_set'),
    path('change_mobile/', views.MobileChangeView.as_view(), name='change_mobile'),
    path('index/', views.UserIndexView.as_view(), name='user_index'),

]
