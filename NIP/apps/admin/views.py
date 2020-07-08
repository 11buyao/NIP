import json
from collections import OrderedDict

from django.contrib.auth.models import Group, Permission
# from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect

# Create your views here.
from django.template.response import SimpleTemplateResponse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from NIP.settings import settings
from NIP.utils import ConstantDefinition
from NIP.utils.fastdfs.fdfs import FDFS_Client
from NIP.utils.res_code import to_json_data, Code, error_map
from admin.forms import NewsForm
from admin.paginator import get_page_data
from news import models
from users.models import User
import logging
from datetime import datetime

logger = logging.getLogger('django')


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url='/users/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class PermissionRequiredMixin(object):
    permission_required = None

    # login_url = '403.html'

    def method_to_permission(self, request):
        for permission in self.permission_required:
            if request.method.lower() == 'get':
                if 'view' in permission:
                    return permission
            elif request.method.lower() == 'post':
                if 'add' in permission:
                    return permission
            elif request.method.lower() == 'put':
                if 'change' in permission:
                    return permission
            elif request.method.lower() == 'delete':
                if 'delete' in permission:
                    return permission

    def dispatch(self, request, *args, **kwargs):
        if Group.objects.filter(user=request.user).first():
            user_permissions = Group.objects.filter(user=request.user).first().permissions.all()
            user_permissions = [i.content_type.app_label + '.' + i.codename for i in user_permissions]

            local_permission_required = self.method_to_permission(request)
            if local_permission_required not in user_permissions:
                if request.method.lower() == 'get':
                    return render(request, '403.html', context={'errmsg': '很抱歉,您没有权限使用该功能,请联系管理员申请权限！'})
                return to_json_data(errno=Code.ROLEERR, errmsg='您未拥有权限,请向超管申请', data={'redirect_url': '403.html'})
            return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return render(request, '403.html', context={'errmsg': '很抱歉,您没有权限使用该功能,请联系管理员申请权限！'})


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'admin/news/index.html')


class TagManageView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('news.view_tag', 'news.change_tag', 'news.delete_tag', 'news.add_tag')

    def get(self, request):
        tags = models.Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(is_delete=False)
        return render(request, 'admin/news/tag_manage.html', locals())

    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_str.decode('utf8'))
        name = dict_data.get('name')
        if not name:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        if len(name) > 20:
            return to_json_data(errno=Code.PARAMERR, errmsg='分类名称请控制在20字内')
        tag = models.Tag.objects.get_or_create(name=name)
        if not tag[-1]:
            if tag[0].is_delete:
                tag[0].is_delete = False
                tag[0].save(update_fields=['is_delete'])
                return to_json_data(errno=Code.OK)
            else:
                return to_json_data(errno=Code.DATAEXIST, errmsg='该分类已存在')
        else:
            return to_json_data(errno=Code.OK)

    def put(self, request, tag_id):

        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        name = dict_data.get('name').strip()
        if not name:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        if len(name) > 20:
            return to_json_data(errno=Code.PARAMERR, errmsg='分类名称请控制在20字内')
        tag = models.Tag.objects.get(id=tag_id)
        if tag:
            if not models.Tag.objects.filter(is_delete=False, name=name).exists():
                tag.name = name
                tag.save(update_fields=['name'])
                return to_json_data(errno=Code.OK)
            else:
                return to_json_data(errno=Code.DATAEXIST, errmsg=error_map[Code.DATAEXIST])
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='该分类不存在')

    def delete(self, request):
        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf-8'))
        tag_id = dict_data.get('tag_id')
        if not tag_id:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        if type(tag_id) == type(list()):
            tag_list = []
            for id in tag_id:
                tag = models.Tag.objects.get(is_delete=False, id=id)
                if tag:
                    if models.Tag.objects.values('id').annotate(num_news=Count('news')).filter(is_delete=False, id=id). \
                            get()['num_news']:
                        return to_json_data(errno=Code.NODATA, errmsg='文章数量不为零的分类不允许删除')
                    tag_list.append(tag)
                else:
                    return to_json_data(errno=Code.NODATA, errmsg='分类信息不存在')
            for tag in tag_list:
                tag.is_delete = True
                tag.save(update_fields=['is_delete'])

            return to_json_data(errno=Code.OK)
        else:
            tag = models.Tag.objects.get(id=tag_id)
            if tag:
                if models.Tag.objects.values('id').annotate(num_news=Count('news')).filter(is_delete=False, id=tag_id). \
                        get()['num_news']:
                    return to_json_data(errno=Code.NODATA, errmsg='文章数量不为零的分类不允许删除')
                else:
                    tag.is_delete = True
                    tag.save(update_fields=['is_delete'])
                    return to_json_data(errno=Code.OK)
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='该分类不存在')


class NewsByTagView(View):
    def get(self, request, tag_id):
        news = models.News.objects.values('id', 'title').filter(is_delete=False, tag_id=tag_id)
        news_list = [i for i in news]
        return to_json_data(data={'news': news_list})


class NewsManageView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('news.view_news', 'news.delete_news')

    def get(self, request):
        start_time = request.GET.get('start_time', '')
        start_time = datetime.strptime(start_time, '%Y/%m/%d') if start_time else ''
        end_time = request.GET.get('end_time', '')
        end_time = datetime.strptime(end_time, '%Y/%m/%d') if end_time else ''
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        news = models.News.objects.only('title', 'update_time', 'tag__name', 'author__username').filter(
            is_delete=False)
        if start_time and not end_time:
            news = news.filter(update_time__gte=start_time)
        if not start_time and end_time:
            news = news.filter(update_time__lte=end_time)
        if start_time and end_time:
            news = news.filter(update_time__gte=start_time, update_time__lte=end_time)
        title = request.GET.get('title', '')

        if title:
            news = news.filter(title__icontains=title)
        author = request.GET.get('author', '')
        if author:
            news = news.filter(author__username__icontains=author)
        tags = models.Tag.objects.only('name').filter(is_delete=False)
        tag = int(request.GET.get('tag_id', 0))
        news = news.filter(tag_id=tag, is_delete=False) or news.filter(is_delete=False)
        try:
            page = request.GET.get('page', 1)
        except Exception as e:
            logger.error('页面参数异常：\n{}'.format(e))
            page = 1

        pages = Paginator(news, 10)

        try:
            news_info = pages.page(page)
        except EmptyPage:
            logger.error('页码错误')
            news_info = pages.page(pages.num_pages)
        pages_data = get_page_data(pages, news_info, 1)
        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if start_time else ''

        data = {
            'news': news_info,
            'tags': tags,
            'paginator': pages,
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'author': author,
            'tag_id': tag,
            'other_params': urlencode({
                'start_time': start_time,
                'end_time': end_time,
                'title': title,
                'author': author,
                'tag_id': tag
            })
        }
        data.update(pages_data)
        return render(request, 'admin/news/news_manage.html', context=data)

    def delete(self, request):
        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        news_id = dict_data.get('news_id')
        if type(news_id) == type(list()):
            news_list = []
            for id in news_id:
                news = models.News.objects.filter(is_delete=False, id=id).first()
                if news:
                    news_list.append(news)
                else:
                    return to_json_data(errno=Code.PARAMERR, errmsg='选择的文章中有ID错误')
            for news in news_list:
                news.is_delete = True
                news.save(update_fields=['is_delete'])
            return to_json_data(errno=Code.OK)
        else:
            news = models.News.objects.filter(is_delete=False, id=news_id).first()
            if news:
                news.is_delete = True
                news.save(update_fields=['is_delete'])
                return to_json_data(errmsg='文章删除成功')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='该文章不存在')


class NewsEditView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('news.view_news', 'news.change_news')

    def get(self, request, news_id):
        news = models.News.objects.filter(is_delete=False, id=news_id).first()
        tags = models.Tag.objects.filter(is_delete=False)
        if news:
            data = {
                'news': news,
                'tags': tags
            }
            return render(request, 'admin/news/news_edit.html', context=data)
        # else:
        #     return render(request, '404.html')

    def put(self, request, news_id):
        news = models.News.objects.filter(id=news_id, is_delete=False).first()
        if not news:
            return to_json_data(errno=Code.PARAMERR, errmsg='文章不存在')

        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        form = NewsForm(data=dict_data)
        if form.is_valid():
            news.title = form.cleaned_data.get('title')
            news.digest = form.cleaned_data.get('digest')
            news.tag = form.cleaned_data.get('tag')
            news.content = form.cleaned_data.get('content')
            news.image_url = form.cleaned_data.get('image_url')
            news.save()
            return to_json_data(errmsg='文章更新成功')
        else:
            err_m_l = []
            for i in form.errors.values():
                err_m_l.append(i[0])
            errmsg_str = '/'.join(err_m_l)
            return to_json_data(errno=Code.PARAMERR, errmsg=errmsg_str)


class NewsPubView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('news.view_news', 'news.add_news')

    def get(self, request):
        tags = models.Tag.objects.filter(is_delete=False)
        data = {
            'tags': tags
        }
        return render(request, 'admin/news/news_edit.html', context=data)

    def post(self, request):
        json_str = request.body
        if not json_str:
            to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        dict_data = json.loads(json_str)

        # 数据清洗
        form = NewsForm(data=dict_data)
        if form.is_valid():
            # 对于作者更新对于的新闻, 知道新闻是哪个作者发布的
            # 创建实例  不保存到数据库
            news = models.News.objects.filter(title=form.cleaned_data.get('title'),
                                              content=form.cleaned_data.get('content'),
                                              tag=form.cleaned_data.get('tag'),
                                              digest=form.cleaned_data.get('digest'),
                                              image_url=form.cleaned_data.get('image_url')).first()
            if news:
                news.is_delete = False
                news.save(update_fields=['is_delete'])
            else:
                news = form.save(commit=False)
                news.author_id = request.user.id
                news.save()
            return to_json_data(errmsg='文章发布成功')

        else:
            err_m_l = []
            for i in form.errors.values():
                err_m_l.append(i[0])
            err_msg_str = '/'.join(err_m_l)
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class BannerManageView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('news.view_banners', 'news.change_banners', 'news.delete_banners')

    def get(self, request):
        banners = models.Banners.objects.filter(is_delete=False)
        priority_dict = OrderedDict(models.Banners.B_CHOICES)
        return render(request, 'admin/news/banner_manage.html', locals())

    def put(self, request, banner_id):
        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banners.B_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.NODATA, errmsg='传入的轮播图优先级不存在')
        except Exception as e:
            logger.error('优先级传入异常：{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='传入的优先级参数不合法')
        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.NODATA, errmsg='传入的图片参数为空')
        banner = models.Banners.objects.filter(is_delete=False, id=banner_id).first()
        if banner.priority == priority and banner.image_url == image_url:
            return to_json_data(errno=Code.DATAEXIST, errmsg='传入的图片和优先级和与原轮播图一致')
        if banner:
            banner.priority = priority
            banner.image_url = image_url
            banner.save(update_fields=['priority', 'image_url'])
            return to_json_data(errmsg='轮播图更新成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='轮播图不存在')

    def delete(self, request, banner_id):
        banner = models.Banners.objects.filter(is_delete=False, id=banner_id).first()
        if banner:
            banner.is_delete = True
            banner.save(update_fields=['is_delete'])
            return to_json_data(errmsg='轮播图删除成功')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='该轮播图不存在')


class BannerAddView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('news.view_banners', 'news.add_banners')

    def get(self, request):
        tags = models.Tag.objects.filter(is_delete=False)
        priority_dict = OrderedDict(models.Banners.B_CHOICES)
        return render(request, 'admin/news/banner_add.html', locals())

    def post(self, request):
        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        try:
            priority = int(dict_data.get('priority'))
            priority_list = [i for i, _ in models.Banners.B_CHOICES]
            if priority not in priority_list:
                return to_json_data(errno=Code.PARAMERR, errmsg='轮播图优先级不存在')
        except Exception as e:
            logger.error('轮播图优先级获取异常：{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='优先级获取异常')
        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.NODATA, errmsg='图片URL为空')
        news_id = int(dict_data.get('news_id'))
        if not models.News.objects.filter(is_delete=False, id=news_id).exists():
            return to_json_data(errno=Code.NODATA, errmsg='新闻不存在')
        banner, is_create = models.Banners.objects.get_or_create(news_id=news_id, priority=priority,
                                                                 image_url=image_url)
        if not is_create:
            if banner.is_delete:
                banner.is_delete = False
                banner.save(update_fields=['is_delete'])
                return to_json_data(errmsg='轮播图添加成功')
            else:
                return to_json_data(errno=Code.DATAEXIST, errmsg='该轮播图已存在')
        else:
            return to_json_data(errno=Code.OK)


class GroupManageView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('auth.view_group', 'auth.delete_group')

    def get(self, request):
        groups = Group.objects.values('id', 'name').annotate(num_users=Count('user')).order_by('num_users')
        return render(request, 'admin/users/group_manage.html', locals())

    def delete(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf-8'))

        group_id = dict_data.get('group_list')
        if type(group_id) != type(list()):
            try:
                group_id = int(group_id)
            except Exception as e:
                logger.error('用户组ID传入异常：{}'.format(e))
                return to_json_data(errno=Code.PARAMERR, errmsg='用户组ID异常')
            group = Group.objects.filter(id=group_id).first()
            if group:
                group.permissions.clear()
                group.delete()
                return to_json_data(errmsg='用户组删除成功')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='该用户组不存在')
        else:
            group_list = []
            for id in group_id:
                group = Group.objects.get(id=id)
                if group:
                    if Group.objects.values('id').annotate(num_users=Count('user')).filter(id=id). \
                            get()['num_users']:
                        return to_json_data(errno=Code.NODATA, errmsg='还有用户存在的用户组不允许被删除')
                    group_list.append(group)
                else:
                    return to_json_data(errno=Code.NODATA, errmsg='用户组不存在')
            for group in group_list:
                group.permissions.clear()
                group.delete()

            return to_json_data(errno=Code.OK)


class GroupEditView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('auth.view_group', 'auth.change_group')

    def get(self, request, g_id):
        group = Group.objects.filter(id=g_id).first()
        if group:
            permissions = Permission.objects.all()
            return render(request, 'admin/users/group_edit.html', context={'group': group, 'permissions': permissions})
        else:
            return render(request, '404.html')

    def put(self, request, g_id):
        group = Group.objects.filter(id=g_id).first()
        if not group:
            return to_json_data(errno=Code.PARAMERR, errmsg='该用户组不存在')

        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        name = dict_data.get('name').strip()
        permissions = dict_data.get('group_permission')
        local_group_permissions = set(i.id for i in group.permissions.all())
        try:
            permissions = set(int(i) for i in permissions)
        except Exception as e:
            logger.error('传入的权限参数异常:{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='传入的权限参数异常')
        if not name:
            return to_json_data(errno=Code.PARAMERR, errmsg='请输入用户组名')
        if name != group.name and Group.objects.filter(name=name).exists():
            return to_json_data(errno=Code.DATAEXIST, errmsg='该用户组名已存在')
        permissions.update(local_group_permissions)
        group.permissions.clear()
        for i in permissions:
            p = Permission.objects.get(id=i)
            if not p:
                return to_json_data(errno=Code.PARAMERR, errmsg='传入的权限不合法')
            group.permissions.add(p)

        group.name = name
        group.save()
        return to_json_data(errmsg='用户组更新成功 ')


class GroupAddView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('auth.view_group', 'auth.add_group')

    def get(self, request):
        permissions = Permission.objects.all()
        return render(request, 'admin/users/group_edit.html', locals())

    def post(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        name = dict_data.get('name').strip()
        permissions = dict_data.get('group_permission')
        try:
            permissions = set(int(i) for i in permissions)
        except Exception as e:
            logger.error('传入的权限参数异常:{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='传入的权限参数异常')
        if not name:
            return to_json_data(errno=Code.PARAMERR, errmsg='请输入用户组名')
        group, is_create = Group.objects.get_or_create(name=name)
        if is_create:
            for i in permissions:
                p = Permission.objects.get(id=i)
                if not p:
                    return to_json_data(errno=Code.PARAMERR, errmsg='传入的权限不合法')
                group.permissions.add(p)

            group.save()
            return to_json_data(errmsg='用户组更新成功 ')
        else:
            return to_json_data(errno=Code.PARAMERR, errmsg='组名已存在')


class UserManageView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('users.view_user', 'users.delete_user')

    def get(self, request):
        users = User.objects.only('id', 'username', 'mobile', 'is_staff', 'is_superuser', 'is_active', 'is_VIP').filter(
            is_active=True)
        username = request.GET.get('username', '')
        if username:
            users = users.filter(username__icontains=username, is_active=True)
        mobile = request.GET.get('mobile', '')
        if mobile:
            users = users.filter(mobile__icontains=mobile, is_active=True)
        groups = Group.objects.only('name').all()
        group_id = int(request.GET.get('group_id', 0))

        users = users.filter(groups__name=Group.objects.get(id=group_id).name, is_active=True) if group_id else users
        try:
            page = request.GET.get('page', 1)
        except Exception as e:
            logger.error('页数异常：\n{}'.format(e))
            page = 1
        pages = Paginator(users, 5)
        try:
            users_info = pages.page(page)
        except EmptyPage:
            logger.error('页码错误')
            users_info = pages.page(pages.num_pages)
        pages_data = get_page_data(pages, users_info, 1)

        data = {
            'users': users_info,
            'groups': groups,
            'paginator': pages,
            'username': username,
            'mobile': mobile,
            'group_id': group_id,
            'other_params': urlencode({
                'username': username,
                'mobile': mobile,
                'group_id': group_id,
            })
        }
        data.update(pages_data)
        return render(request, 'admin/users/user_manage.html', context=data)

    def delete(self, request):
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        user_id = dict_data.get('user_list')
        if type(user_id) == type(list()):
            user_list = []
            for i in user_id:
                user = User.objects.filter(is_active=True, id=i).first()
                if user.username == request.user.username:
                    return to_json_data(errno=Code.USERERR, errmsg='用户不能操作自己的权限')
                if user:
                    user_list.append(user)
                else:
                    return to_json_data(errno=Code.PARAMERR, errmsg='有用户不存在')
            for user in user_list:
                user.groups.clear()
                user.user_permissions.clear()
                user.is_active = False
                user.save()
            return to_json_data(errmsg='选中的用户均已被删除')
        else:
            try:
                user_id = int(user_id)
            except Exception as e:
                logger.error('用户id异常：{}'.format(e))
                return to_json_data(errno=Code.PARAMERR, errmsg='用户的id不合法')
            user = User.objects.filter(is_active=True, id=user_id).first()
            if user:
                if user.username == request.user.username:
                    return to_json_data(errno=Code.USERERR, errmsg='用户不能操作自己的权限')
                user.groups.clear()
                user.user_permissions.clear()
                user.is_active = False
                user.save()
                return to_json_data(errmsg='用户删除成功')
            else:
                return to_json_data(errno=Code.PARAMERR, errmsg='该用户不存在')


class UserEditView(PermissionRequiredMixin, LoginRequiredMixin, View):
    permission_required = ('users.view_user', 'users.change_user')

    def get(self, request, user_id):
        user = User.objects.filter(is_active=True, id=user_id).first()
        if user.username == request.user.username:
            # return
            return SimpleTemplateResponse('403.html', {'errmsg': '123'})
        if user:
            groups = Group.objects.all()
            return render(request, 'admin/users/user_edit.html', context={'user_instance': user, 'groups': groups})
        else:
            return render(request, '404.html')

    def put(self, request, user_id):
        user = User.objects.filter(is_active=True, id=user_id).first()
        if user.username == request.user.username:
            return to_json_data(errno=Code.USERERR, errmsg='用户不能操作自己的权限')
        if not user:
            return to_json_data(errno=Code.PARAMERR, errmsg='该用户不存在')
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        is_staff = int(dict_data.get('is_staff'))
        is_superuser = int(dict_data.get('is_superuser'))
        is_active = int(dict_data.get('is_active'))
        is_VIP = int(dict_data.get('is_VIP'))
        groups = dict_data.get('groups')
        if not all([q in [0, 1] for q in (is_staff, is_superuser, is_active, is_VIP)]):
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        try:
            if groups:
                group_set = set(int(i) for i in groups)
            else:
                group_set = set()
        except Exception as e:
            logger.error('传入的用户组参数异常：{}'.format(e))
            return to_json_data(errno=Code.PARAMERR, errmsg='用户组参数异常')
        all_groups_set = set(i.id for i in Group.objects.only('id'))

        if not group_set.issubset(all_groups_set):
            return to_json_data(errno=Code.PARAMERR, errmsg='传入的用户组参数不合法')
        gsa = Group.objects.filter(id__in=group_set)

        user.groups.set(gsa)
        user.is_staff = bool(is_staff)
        user.is_superuser = bool(is_superuser)
        user.is_active = bool(is_active)
        user.is_VIP = bool(is_VIP)
        user.save()
        return to_json_data(errmsg='用户权限信息更新成功')


class UpToServerView(View):
    def post(self, request):
        name = request.FILES
        image_file = name.get('image_files')
        if image_file.content_type not in ConstantDefinition.IMAGE_TYPE_LIST:
            return to_json_data(errno=Code.PARAMERR, errmsg='不能上传非图片文件')
        ext_name = image_file.name.split('.')[-1]
        try:
            upload_img = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=ext_name)
        except Exception as e:
            logger.error('图片上传失败：{}'.format(e))
            return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传失败')
        else:
            if upload_img.get('Status') != 'Upload successed.':
                return to_json_data(errno=Code.UNKOWNERR, errmsg='图片上传到服务器失败')
            else:
                img_id = upload_img.get('Remote file_id')
                img_url = settings.FDFS_URL + img_id
                return to_json_data(data={'image_url': img_url}, errmsg='图片上传成功')


@method_decorator(csrf_exempt, name='dispatch')
class MarkdownUploadView(View):
    def post(self, request):
        image_file = request.FILES.get('editormd-image-file')
        if not image_file:
            logger.error('从前端获取图片失败')
            return JsonResponse({'success': 0, 'message': '从前端获取图片失败'})
        if image_file.content_type not in ConstantDefinition.IMAGE_TYPE_LIST:
            return JsonResponse({'success': 0, 'message': '不能上传非图片文件'})

        try:
            image_ext_name = image_file.name.split('.')[-1]
        except Exception as e:
            logger.error('文件拓展名异常：{}'.format(e))
            image_ext_name = 'jpg'
        try:
            upload_res = FDFS_Client.upload_by_buffer(image_file.read(), file_ext_name=image_ext_name)
        except Exception as e:
            logger.error('图片上传出现异常：{}'.format(e))
            return JsonResponse({'success': 0, 'message': '图片上传失败'})
        else:
            if upload_res.get('Status') != 'Upload successed.':
                logger.error('图片上传到FastFDS服务器失败')
                return JsonResponse({'success': 0, 'message': '图片上传到服务器失败'})
            else:
                image_name = upload_res.get('Remote file_id')
                image_url = settings.FDFS_URL + image_name
                return JsonResponse({'success': 1, 'message': '图片上传成功', 'url': image_url})
