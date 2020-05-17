from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumExpandMethod, ReadDetail
from django.contrib.contenttypes.fields import GenericRelation

class BlogType(models.Model):
    type_name = models.CharField(max_length=15)     # 博客类型

    def __str__(self):
        return self.type_name


class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=50)     # 博客名字
    blog_type = models.ForeignKey(BlogType, on_delete=models.DO_NOTHING, related_name="blog")   # 关联类型
    content = RichTextUploadingField()    # 博客内容
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)   # 博客作者
    read_details = GenericRelation(ReadDetail)
    created_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    last_updated_time = models.DateTimeField(auto_now=True)     # 最后修改时间

    def get_url(self):
        return reverse("blog:blog_detail", kwargs={"blog_pk": self.pk})

    def get_email(self):
        return self.author.email

    def __str__(self):
        return "<Blog: %s>" % self.title
    class Meta:
        ordering = ["-created_time"]


# class ReadNum(models.Model):
#     read_num = models.IntegerField(default=0)  # 阅读数量统计
#     blog = models.OneToOneField(Blog, on_delete=models.DO_NOTHING)  # 一对一，一条博客只对应一条阅读量信息





