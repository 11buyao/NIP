import json

import re
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from news.models import Comments, ThumbsUpClicks, News
from users.forms import LoginForm
from users.models import User
from NIP.utils.res_code import to_json_data, Code, error_map


class RegisterView(View):
    def get(self, request):
        request.session['referer'] = request.META.get('HTTP_REFERER', '')
        return render(request, 'users/register.html')

    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))

        username = dict_data.get('username')
        mobile = dict_data.get('mobile')
        password = dict_data.get('password')
        password_repeat = dict_data.get('password_repeat')
        smsCode = dict_data.get('smsCode')

        if not all([username, mobile, password, password_repeat, smsCode]):
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')

        # 验证用户名
        if not re.match(r'^[\u4e00-\u9fa5\w\d_]{2,20}$', username):
            return to_json_data(errno=Code.PARAMERR, errmsg='用户名格式不正确')
        if User.objects.filter(username=username).count() > 0:
            return to_json_data(errno=Code.DATAEXIST, errmsg='用户名已存在')
        # 验证手机号
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return to_json_data(errno=Code.PARAMERR, errmsg='手机号格式不正确')
        if User.objects.filter(mobile=mobile).count() > 0:
            return to_json_data(errno=Code.DATAEXIST, errmsg='手机号已存在')
        # 验证密码
        if not re.match(r'^[\w\d]{6,20}', password):
            return to_json_data(errno=Code.PARAMERR, errmsg='密码格式不正确')
        if password != password_repeat:
            return to_json_data(errno=Code.PARAMERR, errmsg='两次输入的密码不一致，请重新输入')
        # 验证码校验
        redis_conn = get_redis_connection('verify_codes')
        sms_code = redis_conn.get('sms_{}'.format(mobile))
        if not sms_code:
            return to_json_data(errno=Code.NODATA, errmsg='验证码已过期，请重新获取')
        if sms_code.decode() != smsCode:
            return to_json_data(errno=Code.PARAMERR, errmsg='验证码输入错误，请重新输入')
        redis_conn.delete('sms_{}'.format(mobile))
        redis_conn.delete('sms_flag_{}'.format(mobile))
        user, is_create = User.objects.get_or_create(username=username, password=password, mobile=mobile)
        if is_create:
            login(request, user)

            return to_json_data(errmsg='恭喜您，注册成功', data={'referer': request.session['referer']})
        else:
            if user.is_active:
                return to_json_data(errno=Code.USERERR, errmsg='该用户已被注册')
            else:
                user.is_active = True
                user.save(update_fields=['is_active'])
                login(request, user)
                return to_json_data(errmsg='恭喜您，注册成功')


class LoginView(View):
    def get(self, request):
        request.session['referer'] = request.META.get('HTTP_REFERER', '')
        return render(request, 'users/login.html')

    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))

        form = LoginForm(data=dict_data, request=request)
        if form.is_valid():

            return to_json_data(errmsg='登录成功',
                                data={'referer': request.session['referer'] if (request.session[
                                                                                    'referer'] and request.user.is_staff) else None})
        else:
            # 表单验证失败处理
            msg_list = []
            for i in form.errors.get_json_data().values():
                msg_list.append(i[0].get('message'))
            msg_str = '/'.join(msg_list)
            return to_json_data(errno=Code.PARAMERR, errmsg=msg_str)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('users:login'))


class FindPasswordView(View):
    def get(self, request):
        return render(request, 'users/find_password.html')

    def post(self, request):
        if request.user.is_authenticated:
            return to_json_data(errno=Code.DATAERR, errmsg='用户已登录，请退出登录')
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        mobile = dict_data.get('mobile')
        password = dict_data.get('password')
        password_repeat = dict_data.get('password_repeat')
        smsCodeText = dict_data.get('smsCodeText')
        if not all([mobile, password, password_repeat, smsCodeText]):
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        if not User.objects.filter(mobile=mobile):
            return to_json_data(errno=Code.PARAMERR, errmsg='手机号输入错误')
        if not ((20 >= len(password) >= 6) or (20 >= len(password_repeat) >= 6)):
            return to_json_data(errno=Code.PARAMERR, errmsg='密码长度为6-20位')
        redis_conn = get_redis_connection('verify_codes')
        sms_code = redis_conn.get('sms_{}'.format(mobile))
        if sms_code.decode() != smsCodeText:
            return to_json_data(errno=Code.PARAMERR, errmsg='验证码输入错误')
        redis_conn.delete('sms_flag_{}'.format(mobile))
        redis_conn.delete('sms_{}'.format(mobile))
        user = User.objects.get(mobile=mobile)
        if user:
            user.set_password(password)
            user.save(update_fields=['password'])
            return to_json_data(errmsg='密码修改成功，请重新登录')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='该用户不存在')


class ChangePasswordView(View):
    def get(self, request):
        return render(request, 'users/change_password.html')

    def post(self, request):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.USERERR, errmsg='用户未登录')
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        mobile = dict_data.get('mobile')
        old_pwd = dict_data.get('old_password')
        new_pwd = dict_data.get('password')
        new_pwd_repeat = dict_data.get('password_repeat')
        smsCode = dict_data.get('smsCodeText')
        if not all([mobile, old_pwd, new_pwd, new_pwd_repeat, smsCode]):
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        # 手机号验证
        if not (User.objects.filter(mobile=mobile) and request.user.mobile == mobile):
            return to_json_data(errno=Code.PARAMERR, errmsg='手机号输入错误')
        # 密码验证
        if old_pwd == new_pwd:
            return to_json_data(errno=Code.DATAEXIST, errmsg='新密码和原始密码不能相同')
        if not re.match('^[\w\d]{6,20}$', new_pwd):
            return to_json_data(errno=Code.PARAMERR, errmsg='密码长度为6-20位')
        if new_pwd != new_pwd_repeat:
            return to_json_data(errno=Code.PARAMERR, errmsg='请保持两次新密码输入一致')
        # 验证码校验
        redis_conn = get_redis_connection('verify_codes')
        sms_code = redis_conn.get('sms_{}'.format(mobile))
        if not sms_code:
            return to_json_data(errno=Code.NODATA, errmsg='短信验证码已过期，请重新获取')
        if sms_code.decode() != smsCode:
            return to_json_data(errno=Code.PARAMERR, errmsg='短信验证码输入错误，请重新输入')
        redis_conn.delete('sms_flag_{}'.format(mobile))
        redis_conn.delete('sms_{}'.format(mobile))
        user_qs = User.objects.filter(mobile=mobile)
        if user_qs:
            user = user_qs.first()
            if user.check_password(old_pwd):
                user.set_password(new_pwd)
                user.save(update_fields=['password'])
                return to_json_data(errmsg='修改密码成功')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='原始密码输入错误，请重试')
        else:
            return to_json_data(errno=Code.NODATA, errmsg='该用户不存在')


class UserManageView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'users/user_manage.html')
        else:
            return render(request, '404.html')

    def post(self, request):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.USERERR, errmsg='用户未登录')
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        username = dict_data.get('username')
        avatar_url = dict_data.get('avatar_url')
        if not all([username, avatar_url]):
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        if not re.match(r'^[\w_\u4e00-\u9fa5]{2,20}', username):
            return to_json_data(errno=Code.PARAMERR, errmsg='用户名格式不正确')
        user = request.user
        user.username = username
        user.avatar_url = avatar_url
        user.save(update_fields=['username', 'avatar_url'])
        return to_json_data(errmsg='用户信息更新成功')


class MobileChangeView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.USERERR, errmsg='用户未登录')
        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf-8'))
        mobile = dict_data.get('mobile')
        smsCode = dict_data.get('sms_code')
        if not all([mobile, smsCode]):
            return to_json_data(errno=Code.PARAMERR, errmsg='输入的信息为空')
        # 手机号校验

        if User.objects.filter(mobile=mobile).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='该手机号已绑定，请更换其他的手机号')
        if not re.match(r'^1[345789]\d{9}$', mobile):
            return to_json_data(errno=Code.PARAMERR, errmsg='手机号格式不正确')
        # 验证码校验
        redis_conn = get_redis_connection('verify_codes')
        sms_code = redis_conn.get('sms_{}'.format(mobile))
        if not sms_code:
            return to_json_data(errno=Code.NODATA, errmsg='短信验证码已过期，请重新获取')
        if sms_code.decode() != smsCode:
            return to_json_data(errno=Code.PARAMERR, errmsg='短信验证码输入错误，请重新输入')
        redis_conn.delete('sms_flag_{}'.format(mobile))
        redis_conn.delete('sms_{}'.format(mobile))
        user = request.user
        user.mobile = mobile
        user.save(update_fields=['mobile'])
        return to_json_data(errmsg='手机号修改成功')


class UserIndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            comments = Comments.objects.filter(author_id=request.user.id, is_delete=False).order_by('-update_time')
            thumb_up = ThumbsUpClicks.objects.filter(author_id=request.user.id, is_delete=False).order_by(
                '-update_time')
            comment_list = []
            for comment in comments:
                comment_list.append({
                    'content': comment.content,
                    'update_time': comment.update_time,
                    'news': comment.news,
                    'news_comment_count': Comments.objects.filter(news_id=comment.news_id, is_delete=False).count(),
                    'news_thumb_count': sum(i for i in [i.clicks for i in
                                                        Comments.objects.only('clicks').filter(news_id=comment.news_id,
                                                                                               is_delete=False)])
                })
            for thumb in thumb_up:
                comment_list.append(thumb)
            for i in range(len(comment_list) - 1):
                try:
                    a = comment_list[i].update_time
                except AttributeError:
                    a = comment_list[i]['update_time']
                try:
                    b = comment_list[i + 1].update_time
                except AttributeError:
                    b = comment_list[i + 1]['update_time']
                if a < b:
                    comment_list[i], comment_list[i + 1] = comment_list[i + 1], comment_list[i]
            article_count = News.objects.filter(author_id=request.user.id, is_delete=False).count()
            thumb_count = ThumbsUpClicks.objects.filter(author_id=request.user.id, is_delete=False).count()
            return render(request, 'users/index.html',
                          context={'comments': comment_list, 'article_count': article_count,
                                   'thumb_count': thumb_count})
        else:
            return render(request, '404.html')
