from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=CKEditorWidget('ckeditor_form'),
                           error_messages={"required": "评论内容不能为空"})

    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={"id": "reply_comment_id"}))   # 回复的对应的评论的id。attes通过前端页面来获取这个id，用户不可见

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):        # 评论对象验证
        # 判断用户是否登陆
        if self.user.is_authenticated:
            self.cleaned_data["user"] = self.user
        else:
            raise forms.ValidationError("用户尚未登录")

        # 评论对象验证
        content_type = self.cleaned_data["content_type"]
        object_id = self.cleaned_data["object_id"]
        try:
            models_class = ContentType.objects.get(model=content_type).model_class()
            models_obj = models_class.objects.get(pk=object_id)  # 利用id获取对应模型类的具体的博客对象
            self.cleaned_data["content_object"] = models_obj    # 将获得的具体对象赋值给cleaned_data
        except ObjectDoesNotExist:
            raise forms.ValidationError("评论对象不存在")
        return self.cleaned_data

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data["reply_comment_id"]
        if reply_comment_id < 0:
            raise forms.ValidationError("回复出错")
        elif reply_comment_id == 0:
            self.cleaned_data["parent"] = None      # 如果是顶级评论，
        elif Comment.objects.filter(pk=reply_comment_id).exists():      
            self.cleaned_data["parent"] = Comment.objects.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError("回复出错")
        return reply_comment_id

