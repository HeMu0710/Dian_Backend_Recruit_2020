from blog_backend import views
from django.urls import path


urlpatterns = [
    path('blog', views.blog, name='所有博客'),
    path('blog/<int:blog_id>', views.blogRUD, name='博客详情、修改、删除'),
    path('blog/<int:blog_id>/comment', views.comment, name='评论'),
    path('blog/<int:blog_id>/comment/<int:comment_id>', views.deleteComment, name='删除评论'),
    path('blog/add', views.addBlog, name='添加博客'),
]
