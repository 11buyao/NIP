from django.db import models

# Create your models here.
from NIP.utils.models import ModelBase


class Tag(ModelBase):
    """
    文章标签模型类
    """

    name = models.CharField(max_length=20, verbose_name='分类名称')

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_tag'
        verbose_name = '文章分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Banners(ModelBase):
    """轮播图模型类"""
    B_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
        (4, '第四级'),
        (5, '第五级'),
        (6, '第六级'),
    ]

    image_url = models.URLField(verbose_name='轮播图url', help_text='轮播图url')
    priority = models.IntegerField(verbose_name='优先级', help_text='优先级')
    news = models.OneToOneField('News', on_delete=models.CASCADE, null=True, choices=B_CHOICES, default=6)

    class Meta:
        ordering = ['priority', '-update_time', '-id']
        db_table = 'tb_banner'
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<轮播图{}>'.format(self.id)


class News(ModelBase):
    """文章模型类"""
    title = models.CharField(max_length=100, verbose_name='文章标题')
    digest = models.CharField(max_length=300, verbose_name='文章摘要')
    content = models.TextField(verbose_name='文章内容')
    clicks = models.IntegerField(default=0, verbose_name='点击量')
    image_url = models.URLField(verbose_name='图片地址', default='')
    tag = models.ForeignKey('Tag', verbose_name='分类', on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey('users.User', verbose_name='文章作者', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_news'
        verbose_name = '新闻'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def increase_click(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])


class Comments(ModelBase):
    """评论模型类"""
    content = models.TextField(verbose_name='评论内容', help_text='评论内容')
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    news = models.ForeignKey('News', on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    clicks = models.IntegerField(verbose_name='点赞数', default=0)

    class Meta:
        ordering = ['-clicks', '-update_time', '-id']
        db_table = 'tb_comment'
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "评论{}".format(self.id)


class ThumbsUpClicks(ModelBase):
    """评论点赞模型类"""
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    comments = models.ForeignKey('Comments', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_thumbs'
        verbose_name = '点赞'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "点赞{}".format(self.id)
