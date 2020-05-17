import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail


class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            self.text,
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=False
        )



class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)  # 通过ContentType获取对应的模型类
    object_id = models.PositiveIntegerField()  # 记录对应模型的主键值
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.DO_NOTHING)   # 谁写的评论  一个模型两个字段同时指向 User 需要使用反向解析

    root = models.ForeignKey("self", null=True, related_name="root_comment", on_delete=models.DO_NOTHING)   # 记录每一条回复的顶级评论是哪一条 null=True 允许为空
    parent = models.ForeignKey("self", null=True, related_name="parent_comment", on_delete=models.DO_NOTHING)   # 指向自己
    reply_to = models.ForeignKey(User, null=True, related_name="replies", on_delete=models.DO_NOTHING)  # 回复的谁   related_name 反向解析名字为 replies


    def send_mail(self):
        # 发送邮件通知
        if self.parent is None:  # 当parent 如果为空，代表是顶级评论
            # 说明这是评论,评论的话发送邮件要获取的是： 博客作者邮箱以及博客内容
            subject = "有人评论你的博客！"
            email = self.content_object.get_email()
        else:
            # 否则就是回复
            subject = "有人回复你的评论"
            email = self.reply_to.email
        if email != "":
            # text = self.text + "\n" + self.content_object.get_url()
            context = {}
            context["comment_text"] = self.text
            context["url"] = self.content_object.get_url()
            text =render_to_string('comment/send_mail.html', context)
            start_mail = SendMail(subject, text, email)
            start_mail.start()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["comment_time"]        # 按照时间










