import hashlib
import jwt

from django.conf import settings
from django.http import JsonResponse

from blog_backend.models import User


def auth_required():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            try:
                auth = request.META.get('HTTP_AUTHORIZATION').split()
            except AttributeError:
                return JsonResponse({"code": 401, "message": "No authenticate header"})
            # 获取token并校验其合法性
            if auth[0].lower() == 'token':
                try:
                    login_info = jwt.decode(auth[1], settings.SECRET_KEY, algorithms=['HS256'])
                    username = login_info.get('data').get('username')
                except jwt.ExpiredSignatureError:
                    return JsonResponse({"status_code": 401, "message": "Token expired"})
                except jwt.InvalidTokenError:
                    return JsonResponse({"status_code": 401, "message": "Invalid token"})
                except jwt.Exception as e:
                    return JsonResponse({"status_code": 401, "message": "Can not get user object"})

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({"status_code": 401, "message": "User Does Not Exist"})

            else:
                return JsonResponse({"status_code": 401, "message": "Not Support Auth Type"})
            # 登录成功
            request
            return view_func(request, user, *args, **kwargs)
        return _wrapped_view
    return decorator


def signup(request):
    add_nickname = request.POST.get('nickname')
    add_username = request.POST.get('username')
    add_password = request.POST.get('password')
    add_email = request.POST.get('email')
    add_region = request.POST.get('region')
    if User.objects.filter(nickname=add_nickname):
        return JsonResponse({"status_code": 400, "message": "The nickname has bean used"})
    if User.objects.filter(username=add_username):
        return JsonResponse({"status_code": 400, "message": "The username has bean used"})
    if User.objects.filter(email=add_email):
        return JsonResponse({"status_code": 400, "message": "The email has bean used"})
    m1 = hashlib.md5()
    m1.update(add_password.encode('utf-8'))
    User.objects.create(nickname=add_nickname, username=add_username, password=m1.hexdigest(),
                        email=add_email, region=add_region)
    return JsonResponse({"status_code": 200, "message": "sign up success"})


def login(request):
    login_type = request.GET.get('login_type')
    user_db = 'db_' + login_type
    login_username = request.POST.get('username')
    login_password = request.POST.get('password')
    m1 = hashlib.md5()
    m1.update(login_password.encode('utf-8'))
    try:
        user = User.objects.using(user_db).get(username=login_username, password=m1.hexdigest())
    except User.DoesNotExist:
        return JsonResponse({"status_code": 403, "message": "user does not exist or password wrong"})
    return JsonResponse({
        "nickname": user.nickname,
        "username": user.username,
        "email": user.email,
        "region": user.region,
        "token": user.token,
    })
