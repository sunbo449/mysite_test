from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields import exceptions
from django.utils import timezone

class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)  # 阅读数量统计
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)   # 通过ContentType获取对应的模型类
    object_id = models.PositiveIntegerField()    # 记录对应模型的主键值
    content_object = GenericForeignKey('content_type', 'object_id')     # 将获取的模型类和对应的主键值关联起来，这样就能获取到主键值对应的数据了


class ReadNumExpandMethod():        # 作为一个基类，用于被其他需要计数的类所继承
    def get_read_num(self):
        try:
            ct = ContentType.objects.get_for_model(self)    # 获取当前实例对象的模型类的名称（字符串格式）
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)   # 使用ReadNum类将当前对象的模型类和id关联起来
            return readnum.read_num         # 返回ReadNum中具有的阅读数量统计字段的方法
        except exceptions.ObjectDoesNotExist:       # 如果没有获取到
            return 0        # 那么返回 0

class ReadDetail(models.Model):
    date = models.DateField(default=timezone.now)   # 用来记录日期的字段
    read_num = models.IntegerField(default=0)  # 阅读数量统计

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)  # 通过ContentType获取对应的模型类
    object_id = models.PositiveIntegerField()  # 记录对应模型的主键值
    content_object = GenericForeignKey('content_type', 'object_id')  # 将获取的模型类和对应的主键值

