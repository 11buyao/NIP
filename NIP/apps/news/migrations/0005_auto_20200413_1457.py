# Generated by Django 2.1.7 on 2020-04-13 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20200319_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banners',
            name='news',
            field=models.OneToOneField(choices=[(1, '第一级'), (2, '第二级'), (3, '第三级'), (4, '第四级'), (5, '第五级'), (6, '第六级')], default=6, null=True, on_delete=django.db.models.deletion.CASCADE, to='news.News'),
        ),
    ]
