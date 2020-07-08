# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : data_filter.py
# Author: TheWu
# Date  : 2020/4/25

"""

"""
import pytz
from django import template
from datetime import datetime

register = template.Library()


@register.filter()
def time_filter(data):
    if isinstance(data, datetime):
        now = datetime.now()
        now = now.replace(tzinfo=pytz.timezone('UTC'))
        timestamp = (now - data).total_seconds()
        if timestamp < 60:
            return '刚刚'
        elif 60 <= timestamp < (60 * 60):
            minu = int(timestamp // 60)
            return '{}分钟前'.format(minu)
        elif 60 * 60 <= timestamp < (60 * 60 * 24):
            hours = int(timestamp // (60 * 60))
            return '{}小时前'.format(hours)
        elif (60 * 60 * 24) <= timestamp < (60 * 60 * 24 * 30):
            days = int(timestamp // (60 * 60 * 24))
            return '{}天前'.format(days)
        elif (60 * 60 * 24 * 30) <= timestamp < (60 * 60 * 24 * 7 * 52):
            months = int(timestamp // (60 * 60 * 24 * 30))
            return '{}月前'.format(months)
        elif (60 * 60 * 24 * 30 * 7 * 52) <= timestamp < (60 * 60 * 24 * 30 * 7 * 52 * 2):
            years = int(timestamp // (60 * 60 * 24 * 30 * 7 * 52))
            return '{}年前'.format(years)
        else:
            return data.strftime('%Y-%m-%d')
    else:
        return data


@register.filter()
def mobile_filter(data):
    data = data[0:3] + '****' + data[7:]
    return data


@register.filter()
def user_time_filter(data):
    if isinstance(data, datetime):
        now = datetime.now()
        now = now.replace(tzinfo=pytz.timezone('UTC'))
        if data.year == now.year:
            return data.strftime('%m.%d %H:%M')
        else:
            return data.strftime('%Y.%m.%d %H:%M')
    else:
        return data
