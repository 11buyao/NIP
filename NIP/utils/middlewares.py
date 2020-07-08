# ！/usr/bin/env python
# -*- coding:utf-8-*-
# File  : middlewares.py
# Author: TheWu
# Date  : 2020/3/12

"""

"""
import time

from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin

from NIP.settings import settings


class MyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        get_token(request)

        # now_time = time.time()
        # ip = request.META.get('REMOTE_ADDR')
        # black = request.session.get('blackname')
        # if ip == black:
        #     return HttpResponseForbidden('请再五分钟后再访问')
        #     # return HttpResponseRedirect('403.html')
        # else:
        #     if ip not in settings.IP_PULL:
        #         settings.IP_PULL[ip] = [now_time]
        #     history = settings.IP_PULL.get(ip)
        #     while history and now_time - history[-1] > 1:
        #         history.pop()
        #     if len(history) < 10:
        #         history.insert(0, now_time)
        #     else:
        #         request.session['blackname'] = ip
        #         request.session.set_expiry(300)
        #         return HttpResponseForbidden()
