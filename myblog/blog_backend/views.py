from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from blog_backend.models import User, Article

import json

# Create your views here.


def blog(request):
    blog_list = Article.objects.all()
    data = serializers.serialize('json', blog_list,
                                 fields=('article_title', 'article_author', 'created_date', 'edited_date'),
                                 use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse(data, safe=False)


def blogDetail(request, pk):
    article = Article.objects.filter(pk=pk)
    data = serializers.serialize('json', article, use_natural_foreign_keys=True)
    data = json.loads(data)
    return JsonResponse(data, safe=False)


def addBlog(request):
    pass
    # input_dict = request.POST
    # data = json.dumps(input_dict)
    # for article in serializers.deserialize('json', data):
    #     article.save()
    # return JsonResponse(json.loads(serializers.serialize('json', article, use_natural_foreign_keys=True)), safe=False)

