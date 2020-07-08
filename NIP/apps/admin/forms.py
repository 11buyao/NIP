# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : forms.py
# Author: TheWu
# Date  : 2020/4/12

"""

"""
from django import forms
from news import models


class NewsForm(forms.ModelForm):
    image_url = forms.URLField(label='文章缩略图URL', error_messages={'required': '文章缩略图URL不能为空'})
    tag = forms.ModelChoiceField(queryset=models.Tag.objects.only('id').filter(is_delete=False),
                                 error_messages={'required': '文章分类不能为空'})

    class Meta:
        model = models.News
        fields = ['title', 'digest', 'content', 'image_url', 'tag']

        error_messages = {
            'title': {
                'max_length': '文章标题长度不能大于150',
                'min_length': '文章标题长度不能小于1',
                'required': '文章标题不能为空',
            },
            'digest': {
                'max_length': '文章摘要长度不能大于300',
                'min_length': '文章摘要长度不能小于1',
                'required': '文章摘要不能为空',
            },
            'content': {
                'required': '文本内容不能为空',
            }
        }
