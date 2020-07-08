import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Q, Count
from django.shortcuts import render

# Create your views here.
from django.views import View
from haystack.views import SearchView as _SearchView

from NIP.settings import settings
from NIP.utils.res_code import to_json_data, Code, error_map
from NIP.utils.voice_module import VoiceToWord, BaiduVoiceToWord
from news.models import Tag, News, Banners, Comments, ThumbsUpClicks
import logging

from news.templatetags.data_filter import time_filter

logger = logging.getLogger('django')


class IndexView(View):
    def get(self, request):
        tags = Tag.objects.values('id', 'name').annotate(num_news=Count('news')).filter(is_delete=False)
        hot_news = News.objects.only('title', 'image_url', 'update_time', 'clicks').filter(is_delete=False).order_by(
            '-clicks')[0:10]
        num_news = News.objects.filter(is_delete=False).count()
        return render(request, 'news/index.html', context={'tags': tags, 'hot_news': hot_news, 'num_news': num_news})


class NewsListView(View):
    def get(self, request):
        try:
            tag = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.error('页面分类错误{}'.format(e))
            tag = 0
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('页面页数错误{}'.format(e))
            page = 1
        news_list = News.objects.values('title', 'digest', 'image_url', 'update_time', 'clicks', 'id').annotate(
            tag_name=F('tag__name'), author=F('author__username'))
        news_info = news_list.filter(is_delete=False, tag_id=tag) or news_list.filter(is_delete=False)

        # 分页
        pages = Paginator(news_info, 5)
        try:
            news_page = pages.page(page)
        except Exception as e:
            logger.error(e)
            news_page = pages.page(pages.num_pages)
        # print(news_page)
        # print([news['id'] for news in news_page])
        comment_count = []
        # news_list_info = []
        for news in news_page:
            news['update_time'] = time_filter(news['update_time'])

            comment_count.append([i.id for i in Comments.objects.filter(is_delete=False,
                                                                        news_id=news['id'])].__len__())
        data = {
            'news': list(news_page),
            'total_pages': pages.num_pages,

            'comment_count': comment_count

        }
        return to_json_data(data=data)


class BannerView(View):
    def get(self, request):
        banner = Banners.objects.select_related('news').only('image_url', 'news__title').filter(
            is_delete=False).order_by('priority')
        b_info = []
        for i in banner:
            b_info.append({
                'image_url': i.image_url,
                'news_title': i.news.title,
                'news_id': i.news.id
            })
        data = {
            'banner': b_info
        }
        return to_json_data(data=data)


class NewsDetailView(View):
    def get(self, request, news_id):
        title = '详情页'
        news = News.objects.select_related('tag', 'author'). \
            only('title', 'update_time', 'author__username', 'tag__name', 'clicks', 'content'). \
            filter(is_delete=False, id=news_id).first()
        if not news:
            return render(request, '404.html')
        hot_news = News.objects.only('title', 'image_url', 'update_time', 'clicks').filter(is_delete=False).order_by(
            '-clicks')[0:10]
        News.increase_click(news)
        comments = Comments.objects.filter(is_delete=False, news_id=news_id).order_by('-id')

        comment_list = []
        for comment in comments:
            thumbs = ThumbsUpClicks.objects.filter(author_id=request.user.id, comments_id=comment.id,
                                                   is_delete=False).first()
            if thumbs:
                is_thumbs = True if not thumbs.is_delete else False
            else:
                is_thumbs = False

            if not comment.parent_id:
                comment_list.append({
                    'news_id': comment.news_id,
                    'content_id': comment.id,
                    'content': comment.content,
                    'author': comment.author,
                    'update_time': comment.update_time,
                    'is_thumbs': is_thumbs,
                    'clicks': comment.clicks if comment.clicks != 0 else "赞",
                    'child_list': []
                })
        for one_comment in comments:
            if one_comment.parent:
                for parent_comment in comment_list:
                    if one_comment.parent_id == parent_comment['content_id']:
                        parent_comment['child_list'].append(one_comment)
        num_news = News.objects.filter(is_delete=False).count()

        return render(request, 'news/news_detail.html',
                      context={'news': news, 'title': title, 'hot_news': hot_news,
                               'comment_list': comment_list, 'num_news': num_news})


class ThumbsUpView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg='请登录之后再操作')
        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        dict_data = json.loads(json_str.decode('utf8'))
        comment_id = dict_data.get('comment_id')

        if not comment_id:
            return to_json_data(errno=Code.PARAMERR, errmsg='参数错误')
        comment = Comments.objects.filter(is_delete=False, id=comment_id).first()
        if not comment:
            return to_json_data(errno=Code.PARAMERR, errmsg='该评论不存在')
        is_add = ThumbsUpClicks.objects.filter(comments_id=comment_id, author_id=request.user.id).first()
        if is_add:
            if not is_add.is_delete:
                try:
                    if comment.clicks == 0:
                        raise Exception('点赞数异常')
                except Exception as e:
                    logger.error(e)
                    return to_json_data(errno=Code.PARAMERR, errmsg='点赞数异常')
                comment.clicks -= 1
                comment.save(update_fields=['clicks'])
                is_add.is_delete = True
                is_add.save(update_fields=['is_delete'])
                data = {
                    'clicks': comment.clicks if comment.clicks != 0 else "赞",
                    'is_add': False
                }
                # return to_json_data(data=comment.clicks)
            else:
                comment.clicks += 1
                comment.save(update_fields=['clicks'])
                is_add.is_delete = False
                is_add.save(update_fields=['is_delete'])
                data = {
                    'clicks': comment.clicks if comment.clicks != 0 else "赞",
                    'is_add': True
                }
        else:
            comment.clicks += 1
            comment.save(update_fields=['clicks'])
            thumbs = ThumbsUpClicks()
            thumbs.comments_id = comment_id
            thumbs.author_id = request.user.id
            thumbs.save()
            data = {
                'clicks': comment.clicks if comment.clicks != 0 else "赞",
                'is_add': True
            }
        return to_json_data(data=data)


class CommentsView(View):
    def post(self, request, news_id):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg=error_map[Code.SESSIONERR])
        if not News.objects.filter(is_delete=False, id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])

        json_str = request.body
        if not json_str:
            return to_json_data(errno=Code.PARAMERR, errmsg=error_map[Code.PARAMERR])
        dict_data = json.loads(json_str.decode('utf8'))

        content = dict_data.get('content')
        parent_id = dict_data.get('parent_id')
        if not content:
            return to_json_data(errno=Code.NODATA, errmsg='请填写评论内容')
        if parent_id is not None and not Comments.objects.filter(is_delete=False, id=parent_id,
                                                                 news_id=news_id).exists():
            return to_json_data(errno=Code.PARAMERR, errmsg='评论信息不存在')

        comment = Comments()
        comment.news_id = news_id
        comment.content = content
        comment.author = request.user
        comment.parent_id = parent_id
        comment.save()
        return to_json_data(errmsg='评论成功')


class SearchView(_SearchView):
    template = 'news/list.html'

    def create_response(self):
        query = self.request.GET.get('q', '')
        if not query:
            show = True
            hot_news = News.objects.only('title', 'image_url', 'update_time', 'clicks').filter(
                is_delete=False).order_by(
                '-clicks')[0:10]
            news = News.objects.only('title', 'image_url', 'author__username', 'tag__name', 'digest',
                                     'update_time').filter(
                is_delete=False)
            pages = Paginator(news, settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE)
            num_news = News.objects.filter(is_delete=False).count()
            try:
                page = pages.page(int(self.request.GET.get('page', 1)))
            except PageNotAnInteger:
                page = pages.page(int(1))
            except EmptyPage:
                page = pages.page(pages.num_pages)
            return render(self.request, self.template, locals())

        else:
            show = False
            hot_news = News.objects.only('title', 'image_url', 'update_time', 'clicks').filter(
                is_delete=False).order_by(
                '-clicks')[0:10]
            context = self.get_context()
            num_news = News.objects.filter(is_delete=False).count()
            return render(self.request, self.template, locals())


class WordToVoiceView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return to_json_data(errno=Code.SESSIONERR, errmsg='用户未登录')
        if not request.user.is_VIP:
            return to_json_data(errno=Code.DATAERR, errmsg='该用户暂未拥有该权限，请联系管理员进行修改后在进行操作')
        json_str = request.body

        if not json_str:
            return to_json_data(errno=Code.NODATA, errmsg='没有参数')

        dict_data = json.loads(json_str.decode('utf8'))
        words = dict_data.get('words').strip()
        if not words:
            return to_json_data(errno=Code.NODATA, errmsg='未传入参数')
        try:
            per = int(dict_data.get('per'))
            per = per if per else 5
        except Exception as e:
            logger.error('人声选择传参异常：{}'.format(e))
            per = 5
        try:
            speed = int(dict_data.get('speed'))
            speed = speed if speed else 5
        except Exception as e:
            logger.error('语速传参异常：{}'.format(e))
            speed = 5
        try:
            column = int(dict_data.get('column'))
            column = column if column else 5
        except Exception as e:
            logger.error('音调传参异常：{}'.format(e))
            column = 5
        song_length = int(dict_data.get('song_length'))
        engine = BaiduVoiceToWord()
        if song_length == 0:
            result = engine.say_words(words, per=per, pit=column, spd=speed)
        else:
            result = engine.stop()
        if result.get('err_msg'):
            return to_json_data(errno=Code.UNKOWNERR, errmsg='播放错误')
        return to_json_data(errno=Code.OK, data={'song_length': result['song_length']})
