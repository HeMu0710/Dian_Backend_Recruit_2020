from django.db import models
from django.core import serializers
import random


class UserManager(models.Manager):
    def get_by_natural_key(self, nickname):
        return self.get(nickname=nickname)


class User(models.Model):
    nickname = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def __str__(self):
        return self.nickname

    def natural_key(self):
        return self.nickname


class Article(models.Model):
    article_title = models.CharField(max_length=100)
    article_author = models.ForeignKey(User, on_delete=models.CASCADE)
    article_content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    edited_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.article_title


class comment(models.Model):
    comment_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_content = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
