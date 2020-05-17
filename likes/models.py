from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class LikeCount(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 通过ContentType获取对应的模型类
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')			# 记录被点赞的对象

    liked_num = models.IntegerField(default=0)		# 点赞的数量


class LikeRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 通过ContentType获取对应的模型类
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')		# 记录被点赞的对象

    user = models.ForeignKey(User, on_delete=models.CASCADE)   # 记录被点赞用户信息
    liked_time = models.DateTimeField(auto_now_add=True)   # 记录点赞时间



