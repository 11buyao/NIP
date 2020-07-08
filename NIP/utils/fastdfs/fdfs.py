# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : fdfs.py
# Author: TheWu
# Date  : 2020/4/12

"""

"""
from fdfs_client.client import Fdfs_client

# 指定fdfs客户端配置文件所在路径
from NIP.settings import settings

FDFS_Client = Fdfs_client(settings.FDFS_CLIENT_CONF)
