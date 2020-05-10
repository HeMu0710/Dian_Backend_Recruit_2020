import datetime
import jwt
from django.db import models
from django.conf import settings


class UserManager(models.Manager):
    def get_by_natural_key(self, nickname):
        return self.get(nickname=nickname)


class User(models.Model):
    nickname = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

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


class Article(models.Model):
    article_title = models.CharField(max_length=100)
    article_author = models.ForeignKey(User, on_delete=models.CASCADE)
    article_content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    edited_date = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Article, self).save(using='db_' + self.article_author.region)

    def __str__(self):
        return self.article_title


class comment(models.Model):
    comment_article = models.ForeignKey(Article, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_content = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)
