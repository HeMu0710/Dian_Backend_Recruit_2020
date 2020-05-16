from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.core.paginator import Paginator
from django.conf import settings
from blog_backend.models import User, Article, Comment, Tag
from auth_jwt.views import auth_required

import json, datetime


@auth_required()
def blog(request, _):
    # 根据用户region选择对应的数据库，之后操作同理
    db = request.session['blog_type']
    page_number = request.GET.get('page')
    blog_all = Article.objects.using(db).all()
    pager = Paginator(blog_all, 5)
    data = serializers.serialize('json', pager.page(page_number),
                                 fields=('article_title', 'article_author', 'created_date',
                                         'edited_date', 'tags'), use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse({
        "success": True,
        "status_code": 200,
        "data": data,
    }, status=200)


@auth_required()
def search(request, user):
    # 实现全局搜索
    db = request.session['blog_type']
    page_number = request.GET.get('page')
    keyword = request.GET.get('keyword')
    search_result_list = Article.objects.using(db).filter(
        Q(article_title__icontains=keyword) | Q(article_author__nickname__icontains=keyword)
        | Q(article_content__icontains=keyword) | Q(tags__tag_name__icontains=keyword)
        | Q(article_author__email__icontains=keyword) | Q(article_author__username__icontains=keyword)
        | Q(comment__comment_content__icontains=keyword))
    search_result_list = list(set(search_result_list))
    pager = Paginator(search_result_list, 5)
    result = serializers.serialize('json', pager.page(page_number),
                                   fields=('article_title', 'article_author', 'created_date', 'edited_date', 'tags'),
                                   use_natural_foreign_keys=True)
    result = json.loads(result)
    return JsonResponse({
        "success": True,
        "status_code": 200,
        "data": {
            "keyword": keyword,
            "result_nums": len(search_result_list),
            "results": result,
        }
    }, status=200)


@auth_required()
def blogRUD(request, user, blog_id):
    db = request.session['blog_type']
    article = Article.objects.using(db).get(pk=blog_id)

    # R,展示博客内容
    if request.method == 'GET':
        article.click_nums += 1
        article.save()
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
            article.edited_date = datetime.datetime.now()
            article.save()
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
            for tag in article.tags.all():
                tag.related_article_nums -= 1
                if tag.related_article_nums <= 0:
                    tag.delete()
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
def addBlog(request, user):
    db = request.session['blog_type']
    # 创建博客
    add_article_title = request.POST.get('article_title')
    add_article_content = request.POST.get('article_content')

    add_article = Article.objects.using(db).create(article_title=add_article_title,
                                                   article_content=add_article_content,
                                                   article_author=user,
                                                   edited_date=datetime.datetime.now())
    add_article_tags = request.POST.get('article_tags').split()
    for tag_name in add_article_tags:
        try:
            tag = Tag.objects.using(db).get(tag_name=tag_name)
        except Tag.DoesNotExist:
            tag = Tag.objects.using(db).create(tag_name=tag_name)

        add_article.tags.add(tag)
        tag.related_article_nums += 1
        tag.save()

    return JsonResponse({
        "success": True,
        "status_code": 201,
        "data": {}
    }, status=201)


@auth_required()
def comment(request, user, blog_id):
    db = request.session['blog_type']
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
    db = request.session['blog_type']
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
def like(request, user, blog_id):
    db = request.session['blog_type']
    article = Article.objects.using(db).get(pk=blog_id)
    article.liked_times += 1
    article.save()
    return JsonResponse({
        "success": True,
        "status_code": 200,
        "data": {},
    }, status=200)
