# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : tasks.py
# Author: TheWu
# Date  : 2020/3/1

"""

"""
import logging

from NIP.utils.yuntongxun.sms import CCP
from celery_tasks.main import celery_app

logger = logging.getLogger('django')


@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    """
    :param self:
    :param mobile: 手机号
    :param sms_code:  短信验证码
    :return:
    """
    try:
        send_res = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    except Exception as e:
        logger.error(e)
        raise self.retry(exc=e, max_retries=3)
    if send_res != 0:
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)
    return send_res
