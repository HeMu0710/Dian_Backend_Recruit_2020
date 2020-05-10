from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from blog_backend.models import User, Article
from auth_jwt.views import auth_required

import json, jwt


@auth_required()
def blog(request, user):
    db = 'db_' + user.region
    blog_list = Article.objects.using(db).all()
    data = serializers.serialize('json', blog_list,
                                 fields=('article_title', 'article_author', 'created_date', 'edited_date'),
                                 use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse(data, safe=False)


@auth_required()
def blogRUD(request, user, pk):
    db = 'db_' + user.region
    article = Article.objects.filter(pk=pk)

    # R,展示博客内容
    if request.method == 'GET':
        data = serializers.serialize('json', article, use_natural_foreign_keys=True)
        data = json.loads(data)
        return JsonResponse(data, safe=False)

    # U,更新（修改）博客
    if request.method == 'POST':
        # 检查当前用户是否为博客的作者
        if article.first().article_author == user:
            article.first().article_title = request.POST.get('article_title')
            article.first().article_content = request.POST.get('article_content')
            article.first().save(using=db)
            return JsonResponse({"status_code": 200, "message": "edit article success"})
        else:
            return JsonResponse({"status_code": 403, "message": "No right to edit"})

    # D,删除博客
    if request.method == 'DELETE':
        # 检查当前用户是否为博客的作者
        if article.first().article_author == user:
            article.first().delete()
            return JsonResponse({"status_code": 200, "message": "delete success"})
        else:
            return JsonResponse({"status_code": 403, "message": "No right to delete"})


@auth_required()
def addBlog(request, user):
    db = 'db_' + user.region
    add_article_title = request.POST.get('article_title')
    add_article_content = request.POST.get('article_content')
    Article.objects.using(db).create(article_title=add_article_title,
                                     article_content=add_article_content, article_author=user)
    return JsonResponse({"status_code": 200, "message": "create article success"})


# @auth_required()
# def editBlog(request, user, pk):
#     db = 'db_' + user.region
#     edit_article_title = request.POST.get('article_title')
#     edit_article_content = request.POST.get('article_content')
#     Article.objects.using(db).filter(id=pk).update(article_title=edit_article_title,
#                                                    article_content=edit_article_content)
#     return JsonResponse({"status_code": 200, "message": "edit article success"})
#
#
# @auth_required
# def deleteBlog(request, user, pk):
#     db = 'db_' + user.region
