from django.db import models
import random


class User(models.Model):
    nickname = models.CharField(max_length=50, default='user' + str(random.randint(1000, 9999)), name='用户昵称')
    username = models.CharField(max_length=50, unique=True, name='用户名')
    password = models.CharField(max_length=50, name='用户密码（加密后）')
    region = models.CharField(max_length=50, name='所在地区')
    email = models.EmailField(unique=True, name='用户邮箱')
    created_date = models.DateTimeField(auto_now_add=True, name='注册日期')

    def __str__(self):
        return self.nickname


class Article(models.Model):
    title = models.CharField(max_length=100, name='文章标题')
    author = models.ForeignKey(User, on_delete=models.CASCADE, name='文章作者')
    content = models.TextField(name='文章内容')
    created_date = models.DateTimeField(auto_now_add=True, name='创建日期')
    edited_date = models.DateTimeField(auto_now=True, name='上次修改日期')


class comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, name='被评论文章')
    speaker = models.ForeignKey(User, on_delete=models.CASCADE, name='评论用户')
    comment = models.TextField(name='评论内容')
    created_date = models.DateTimeField(auto_now_add=True, name='评论时间')
