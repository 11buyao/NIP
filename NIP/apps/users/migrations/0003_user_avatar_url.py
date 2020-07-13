# Generated by Django 2.1.7 on 2020-04-27 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200418_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar_url',
            field=models.URLField(default='/static/images/avatar.jpeg', null=True, verbose_name='用户头像URL'),
        ),
    ]