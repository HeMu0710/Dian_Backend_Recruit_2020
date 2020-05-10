from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from blog_backend.models import User, Article
from auth_jwt.views import auth_required

import json, jwt


@auth_required()
def blog(request, user):
    blog_list = Article.objects.using('db_' + user.region).all()
    data = serializers.serialize('json', blog_list,
                                 fields=('article_title', 'article_author', 'created_date', 'edited_date'),
                                 use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse(data, safe=False)


@auth_required()
def blogDetail(request, _, pk):
    article = Article.objects.filter(pk=pk)
    data = serializers.serialize('json', article, use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse(data, safe=False)


@auth_required()
def addBlog(request, user):
    add_article_title = request.POST.get('article_title')
    add_article_content = request.POST.get('article_content')
    Article.objects.create(article_title=add_article_title, article_content=add_article_content,article_author=user)
    return JsonResponse({"status_code": 200, "message": "create article success"})

