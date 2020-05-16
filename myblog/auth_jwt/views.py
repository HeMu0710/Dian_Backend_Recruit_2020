import hashlib
import jwt

from django.conf import settings
from django.http import JsonResponse

from blog_backend.models import User


def auth_required():
    """
    用户认证装饰器
    :return:
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            try:
                auth = request.META.get('HTTP_AUTHORIZATION').split()
            except AttributeError:
                # 无认证信息
                return JsonResponse({
                    "success": False,
                    "status_code": 401,
                    "data": {
                        "message": "No Authenticate Header",
                    },
                }, status=401)
            # 获取token并校验其合法性
            if auth[0].lower() == 'token':
                try:
                    login_info = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
                    username = login_info.get('data').get('username')
                except jwt.ExpiredSignatureError:
                    return JsonResponse({
                        "success": False,
                        "status_code": 401,
                        "data": {
                            "message": "Token Expired",
                        },
                    }, status=401)
                except jwt.InvalidTokenError:
                    return JsonResponse({
                        "success": False,
                        "status_code": 401,
                        "data": {
                            "message": "Invalid Token",
                        },
                    }, status=401)
                except jwt.Exception as e:
                    return JsonResponse({
                        "success": False,
                        "status_code": 401,
                        "data": {
                            "message": "Can not Get User Object",
                        },
                    }, status=401)
                try:
                    db = 'db_' + login_info.get('data').get('region')
                    user = User.objects.using(db).get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({
                        "success": False,
                        "status_code": 401,
                        "data": {
                            "message": "User Does Not Exist",
                        },
                    }, status=401)

            else:
                return JsonResponse({
                    "success": False,
                    "status_code": 401,
                    "data": {
                        "message": "Not Support Auth Type",
                    },
                }, status=401)
            # 登录成功
            return view_func(request, user, *args, **kwargs)

        return _wrapped_view

    return decorator


def signup(request):
    """
    注册
    :param request:
    :return:
    """
    add_nickname = request.POST.get('nickname')
    add_username = request.POST.get('username')
    add_password = request.POST.get('password')
    add_email = request.POST.get('email')
    add_region = request.GET.get('blog_type')
    # 设置地区对应的数据库
    db = 'db_' + add_region
    # 检测注册信息合法性
    if User.objects.using(db).filter(nickname=add_nickname):
        return JsonResponse({
            "success": False,
            "status_code": 400,
            "data": {
                "message": "The nickname has bean used",
            },
        }, status=400)
    if User.objects.using(db).filter(username=add_username):
        return JsonResponse({
            "success": False,
            "status_code": 400,
            "data": {
                "message": "The username has bean used",
            },
        }, status=400)
    if User.objects.using(db).filter(email=add_email):
        return JsonResponse({
            "success": False,
            "status_code": 400,
            "data": {
                "message": "The email has bean used",
            },
        }, status=400)
    # 对密码进行md5加密
    m1 = hashlib.md5()
    m1.update(add_password.encode('utf-8'))
    User.objects.create(nickname=add_nickname, username=add_username, password=m1.hexdigest(),
                        email=add_email, region=add_region)
    return JsonResponse({
        "success": True,
        "status_code": 200,
        "data": {
            "nickname": add_nickname,
            "username": add_username,
            "region": add_region,
        },
    }, status=200)


def login(request):
    """
    登录
    :param request:
    :return:
    """
    # 登录对应地区
    blog_type = request.GET.get('blog_type')
    user_db = 'db_' + blog_type
    login_username = request.POST.get('username')
    login_password = request.POST.get('password')
    m1 = hashlib.md5()
    m1.update(login_password.encode('utf-8'))
    try:
        user = User.objects.using(user_db).get(username=login_username, password=m1.hexdigest())
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "status_code": 403,
            "data": {
                "message": "user does not exist or password wrong",
            },
        }, status=403)
    request.session['blog_type'] = 'db_' + user.region
    return JsonResponse({
        "success": True,
        "status_code": 200,
        "data": {
            "user": {
                "nickname": user.nickname,
                "username": user.username,
                "email": user.email,
                "region": user.region,
            },
            "token": user.token,
        }
    }, status=200)
