# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : forms.py
# Author: TheWu
# Date  : 2020/3/12

"""

"""
import re
from django import forms
from django.contrib.auth import login
from django.db.models import Q

from users.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(max_length=20, min_length=6, error_messages={
        'min_length': '密码长度不能小于6位',
        'max_length': '密码长度不能大于20位',
        'required': '密码长度不能为空',
    })
    remember = forms.BooleanField(required=False)

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(**kwargs)

    def clean_username(self):
        user_info = self.cleaned_data.get('username')
        if not user_info:
            raise forms.ValidationError('用户名不能为空')
        if not re.match(r'^[\u4e00-\u9fa5\w_]{2,20}$', user_info):
            raise forms.ValidationError('用户名格式不正确')
        return user_info

    def clean(self):
        clean_data = super().clean()
        user_info = clean_data.get('username')
        password = clean_data.get('password')
        rm = clean_data.get('remember')
        user_qs = User.objects.filter(Q(mobile=user_info) | Q(username=user_info))
        if user_qs:
            user = user_qs.first()
            # 判断密码
            if user.check_password(password):
                if rm:
                    self.request.session.set_expiry(None)
                else:
                    self.request.session.set_expiry(0)
                login(self.request, user)
            else:
                raise forms.ValidationError('用户名或密码错误，请重新输入')
        else:
            raise forms.ValidationError('用户名不存在，请重新输入')

        return clean_data
