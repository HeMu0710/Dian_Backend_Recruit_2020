from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from blog_backend.models import User, Article, Comment
from auth_jwt.views import auth_required

import json


@auth_required()
def blog(request, user):
    # 根据用户region选择对应的数据库，之后操作同理
    db = 'db_' + user.region
    blog_list = Article.objects.using(db).all()
    data = serializers.serialize('json', blog_list,
                                 fields=('article_title', 'article_author', 'created_date', 'edited_date'),
                                 use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse({
        "success": True,
        "status_code": 200,
        "data": data
    }, status=200)


@auth_required()
def blogRUD(request, user, blog_id):
    db = 'db_' + user.region
    article = Article.objects.using(db).get(pk=blog_id)

    # R,展示博客内容
    if request.method == 'GET':
        blog_data = serializers.serialize('json', [article], use_natural_foreign_keys=True)
        blog_data = json.loads(blog_data)
        comments = Comment.objects.using(db).filter(comment_article=article)
        comments_data = serializers.serialize('json', comments,
                                              fields=('comment_user', 'comment_content', 'comment_date'),
                                              use_natural_foreign_keys=True)
        comments_data = json.loads(comments_data)
        return JsonResponse({
            "success": True,
            "status_code": 200,
            "data": {
                "blog_data": blog_data,
                "comments_data": comments_data,
            },
        }, status=200)

    # U,更新（修改）博客
    if request.method == 'POST':
        # 检查当前用户是否为博客的作者
        if article.article_author == user:
            article.article_title = request.POST.get('article_title')
            article.article_content = request.POST.get('article_content')
            article.save(using=db)
            return JsonResponse({
                "success": True,
                "status_code": 200,
                "data": {},
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "status_code": 403,
                "data": {
                    "message": "No Right to Edit",
                },
            }, status=403)

    # D,删除博客
    if request.method == 'DELETE':
        # 检查当前用户是否为博客的作者
        if article.article_author == user:
            article.delete()
            return JsonResponse({
                "success": True,
                "status_code": 200,
                "data": {
                    "deleted_article_id": blog_id,
                    "deleted_article_title": article.article_title,
                    "deleted_article_author": user.nickname,
                },
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "status_code": 403,
                "data": {
                    "message": "No Right to Delete",
                },
            }, status=403)


@auth_required()
def comment(request, user, blog_id):
    db = 'db_' + user.region
    # 新增评论
    add_comment_content = request.POST.get('comment_content')
    article = Article.objects.using(db).get(pk=blog_id)
    Comment.objects.using(db).create(comment_content=add_comment_content,
                                     comment_user=user.nickname, comment_article=article)
    return JsonResponse({
        "success": True,
        "status_code": 201,
        "data": {},
    }, status=201)


@auth_required()
def deleteComment(request, user, blog_id, comment_id):
    db = 'db_' + user.region
    # 删除评论
    if request.method == 'DELETE':
        delete_comment = Comment.objects.using(db).get(pk=comment_id)
        # 检测当前用户是否有权删除评论，即是否为评论作者或者该文章作者
        if user.nickname == delete_comment.comment_user or \
                user == Article.objects.using(db).get(pk=blog_id).article_author:
            comment_content = delete_comment.comment_content
            comment_author = delete_comment.comment_user
            delete_comment.delete(using=db)
            return JsonResponse({
                "success": True,
                "status_code": 200,
                "data": {
                    "delete_comment_id": comment_id,
                    "delete_comment_content": comment_content,
                    "delete_comment_author": comment_author,
                }
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "status_code": 403,
                "data": {
                    "message": "No Right to Delete",
                },
            }, status=403)


@auth_required()
def addBlog(request, user):
    db = 'db_' + user.region
    # 创建博客
    add_article_title = request.POST.get('article_title')
    add_article_content = request.POST.get('article_content')
    Article.objects.using(db).create(article_title=add_article_title,
                                     article_content=add_article_content, article_author=user)
    return JsonResponse({
        "success": True,
        "status_code": 201,
        "data": {}
        }, status=201)


