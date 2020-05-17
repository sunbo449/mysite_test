from django import forms
from django.contrib.auth.models import User

class ChangeNickForm(forms.Form):
    nickname_new = forms.CharField(
        label="新的昵称",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入新的昵称"})
    )

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):        # 评论对象验证
        # 判断用户是否登陆
        if self.user.is_authenticated:
            self.cleaned_data["user"] = self.user
        else:
            raise forms.ValidationError("用户尚未登录")
        return self.cleaned_data


    def clean_nikename_new(self):
        nickname_new = self.cleaned_data.get("nickname_new", "").strip()
        if nickname_new == "":
            raise forms.ValidationError("新的昵称不能为空")
        return nickname_new


class BinEmailForm(forms.Form):
    email = forms.EmailField(
        label="邮箱",
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'}
        )
    )

    verification_code = forms.CharField(
        label="验证码",
        required=False,  # 设置验证码为不必填写，因为先提交邮箱的时候，还不能填写验证码，如果必填会弹出错误信息
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': "点击'发送验证码'，发送到邮箱"}
        )
    )

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登陆
        if self.request.user.is_authenticated:
            self.cleaned_data["user"] = self.request.user
        else:
            raise forms.ValidationError("用户尚未登录")

        # 判断用户是否已经绑定邮箱
        if self.request.user.email != "":
            raise forms.ValidationError("您已经绑定邮箱！")

        # 验证验证码是否正确
        code = self.request.session.get("bind_email_code", "")   # 取出缓存中生成的验证码
        verification_code = self.cleaned_data.get("verification_code", "")      # 取出用户输入的验证码

        if not(code == verification_code and code != ""):
            raise forms.ValidationError("验证码不正确！")

        return self.cleaned_data

    def clean_email(self):   # 验证邮箱是否已经存在在数据库，
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已经被绑定")
        return email

    def clean_verification_code(self):   # 验证  验证码是否为空
        verification_code = self.cleaned_data.get("verification_code", "").strip()
        if verification_code == "":
            raise forms.ValidationError("验证码不能为空")
        return verification_code












