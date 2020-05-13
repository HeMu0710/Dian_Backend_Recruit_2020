import datetime
import jwt
from django.db import models
from django.conf import settings


class UserManager(models.Manager):
    def get_by_natural_key(self, nickname):
        return self.get(nickname=nickname)


class User(models.Model):
    nickname = models.CharField(max_length=50, unique=True, verbose_name='用户昵称')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')
    region = models.CharField(max_length=50, verbose_name='所属地区')
    email = models.EmailField(unique=True, verbose_name='电子邮箱')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='注册日期')

    objects = UserManager()

    # 重写save方法以保证数据存储到对应地区的数据库
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(User, self).save(using='db_' + self.region)

    def __str__(self):
        return self.nickname

    def natural_key(self):
        return self.nickname

    @property
    def token(self):
        return self._generate_jwt_token()

    # 生成当前用户对应得jwt，过期时间为1天后
    def _generate_jwt_token(self):
        token = jwt.encode({
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'data': {
                'id': self.pk,
                'nickname': self.nickname,
                'username': self.username,
                'region': self.region,
            }
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')

    class Meta:
        verbose_name = '用户'


class Tag(models.Model):
    tag_name = models.CharField(max_length=20, unique=True, primary_key=True, verbose_name='文章标签')
    related_article_nums = models.IntegerField(default=1, verbose_name='相关文章数量')


class Article(models.Model):
    article_title = models.CharField(max_length=100, verbose_name='文章标题')
    article_author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='文章作者')
    article_content = models.TextField(verbose_name='文章内容')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='创建日期')
    edited_date = models.DateTimeField(verbose_name='编辑日期')
    liked_times = models.IntegerField(default=0, verbose_name='被点赞次数')
    click_nums = models.IntegerField(default=0, verbose_name='点击量')
    tags = models.ManyToManyField(Tag, verbose_name='文章标签')

    # 重写save方法以保证数据存储到对应地区的数据库
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Article, self).save(using='db_' + self.article_author.region)

    def __str__(self):
        return self.article_title


class Comment(models.Model):
    comment_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment_user = models.CharField(max_length=50)
    comment_content = models.TextField()
    liked_times = models.IntegerField(default=0)
    comment_date = models.DateTimeField(auto_now_add=True)

