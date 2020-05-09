from blog_backend import views
from django.urls import path


urlpatterns = [
    path('blog', views.blog, name='所有博客'),
    path('blog/<int:pk>', views.blogDetail, name='博客详情'),
    path('blog/add', views.addBlog, name='添加博客')
]
