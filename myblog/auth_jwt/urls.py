from django.urls import path
from auth_jwt import views

urlpatterns = [
    path('signup', views.signup, name='注册'),
    path('login', views.login, name='登录'),
]
