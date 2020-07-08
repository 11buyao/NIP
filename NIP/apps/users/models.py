from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, UserManager as _UserManager


class UserManager(_UserManager):
    """
    用户管理模型类，用户创建管理用户，继承自django auth系统自带的USerManager类
    """

    def create_superuser(self, username, password, email=None, **extra_fields):
        return super().create_superuser(username=username, password=password,
                                        email=email, **extra_fields)


class User(AbstractUser):
    """
    用户模型类，对用户信息表中相关字段进行制定，规范
    """
    REQUIRED_FIELDS = ['mobile']  # 指定注册账户
    objects = UserManager()
    mobile = models.CharField(max_length=11, verbose_name='手机号', unique=True, help_text='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    avatar_url = models.URLField(verbose_name='用户头像URL', null=True, default='/static/images/avatar.jpeg')
    is_VIP = models.BooleanField(default=False, verbose_name='是否是VIP', help_text='是否是VIP')

    class Meta:
        db_table = 'tb_users'
        ordering = ['-id']
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_groups_name(self):
        g_name = (i.name for i in self.groups.all())
        return '/'.join(g_name)
