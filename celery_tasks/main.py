# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : main.py
# Author: TheWu
# Date  : 2020/3/1

"""

"""
from celery import Celery

celery_app = Celery('sms_code')

celery_app.config_from_object('celery_tasks.config')
celery_app.autodiscover_tasks(['celery_tasks.sms'])
