import json
import random
import re

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
import logging

from django_redis import get_redis_connection

from NIP.utils.res_code import to_json_data, Code, error_map
from NIP.utils.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code
from users.models import User
from NIP.utils.captcha.captcha import captcha
from django.views import View

logger = logging.getLogger('django')


class ImageCodeView(View):
    def get(self, request, image_code_id):
        text, image = captcha.generate_captcha()
        con_redis = get_redis_connection(alias='verify_codes')
        img_key = "img_{}".format(image_code_id).encode('utf8')
        con_redis.setex(img_key, 300, text)
        logger.info('Image_code:{}'.format(text))
        return HttpResponse(content_type='image/jpg', content=image)


class CheckUsernameView(View):
    def get(self, request, username):
        data = {
            'username': username,
            'count': User.objects.filter(username=username).count()
        }
        return to_json_data(data=data)


class CheckMobileView(View):
    def get(self, request, mobile):
        data = {
            'mobile': mobile,
            'count': User.objects.filter(mobile=mobile).count()
        }
        return to_json_data(data=data)


class SmsCodeView(View):
    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        text = dict_data.get('text')
        UUID = dict_data.get('image_code_id')
        mobile = dict_data.get('mobile')
        if not all([text, UUID, mobile]):
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return to_json_data(errno=Code.PARAMERR, errmsg='手机号格式不正确')
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get("sms_flag_{}".format(mobile))
        if send_flag:
            return to_json_data(errno=Code.DATAEXIST, errmsg='短信发送频繁，请稍后重试')
        image_code_server = redis_conn.get('img_{}'.format(UUID))
        if not image_code_server:
            return to_json_data(errno=Code.PARAMERR, errmsg='图形验证码已过期，请重新获取')
        try:
            redis_conn.delete("img_{}".format(UUID))
        except Exception as e:
            logger.error(e)
        image_code_server = image_code_server.decode()
        if text.upper() != image_code_server.upper():
            return to_json_data(errno=Code.PARAMERR, errmsg='图形验证码输入错误')
        sms_code = "%06d" % random.randint(0, 999999)
        redis_conn.setex('sms_{}'.format(mobile), 300, sms_code)
        redis_conn.setex('sms_flag_{}'.format(mobile), 60, 1)
        # logger.info('短信验证码发送成功[mobile:{},sms_code:{}]'.format(mobile, sms_code))
        # return to_json_data(errmsg='短信验证码发送成功')
        # # 异步发送短信 需要事先把celery任务开起来才能使用
        # send_res = send_sms_code.delay(mobile, sms_code)
        # print(send_res)
        # if send_res == 0:
        #     return to_json_data(errmsg='短信验证码发送成功')
        # else:
        #     return to_json_data(errno=Code.PARAMERR, errmsg='短信验证码发送失败，请检查手机号你是否正确')
        # 调用接口发送短信
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, 5], 1)
        return to_json_data(errmsg='短信验证码发送成功')

    def put(self, request):

        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))

        mobile = dict_data.get('mobile')
        flag = dict_data.get('flag')
        if not mobile:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        if not flag:
            if not User.objects.filter(mobile=mobile).exists():
                return to_json_data(errno=Code.NODATA, errmsg='该用户不存在，请检查手机号是否输入正确')
        else:
            if User.objects.filter(mobile=mobile).exists():
                return to_json_data(errno=Code.NODATA, errmsg='该手机号已绑定，请输入新的手机号')
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return to_json_data(errno=Code.PARAMERR, errmsg='手机号格式不正确')
        redis_conn = get_redis_connection('verify_codes')
        send_flag = redis_conn.get("sms_flag_{}".format(mobile))
        if send_flag:
            return to_json_data(errno=Code.DATAEXIST, errmsg='短信发送频繁，请稍后重试')

        sms_code = "%06d" % random.randint(0, 999999)
        redis_conn.setex('sms_{}'.format(mobile), 300, sms_code)
        redis_conn.setex('sms_flag_{}'.format(mobile), 60, 1)
        logger.info('短信验证码发送成功[mobile:{},sms_code:{}]'.format(mobile, sms_code))
        return to_json_data(errmsg='短信验证码发送成功')
        # # 异步发送短信 需要事先把celery任务开起来才能使用
        # send_res = send_sms_code.delay(mobile, sms_code)
        # print(send_res)
        # if send_res == 0:
        #     return to_json_data(errmsg='短信验证码发送成功')
        # else:
        #     return to_json_data(errno=Code.PARAMERR, errmsg='短信验证码发送失败，请检查手机号你是否正确')
        # 调用接口发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, 5], 1)
        # return to_json_data(errmsg='短信验证码发送成功')
