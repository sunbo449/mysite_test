from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label="用户名或邮箱",
                               widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入用户名或邮箱"}))
    password = forms.CharField(label="密码",
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入密码"}))

    def clean(self):        # 创建一个验证的方法
        username_or_email = self.cleaned_data["username_or_email"]    # 获取到用户名密码
        password = self.cleaned_data["password"]

        user = authenticate(username=username_or_email, password=password)   # 直接进行验证
        if user is None:    # 如果错误，那么抛出一个异常信息
            if User.objects.filter(email=username_or_email).exists():   # 如果获取到不用户名，那么验证邮箱是否存在
                username = User.objects.get(email=username_or_email).username   # 如果存在，那么根据邮箱取出来这个用户名
                user = authenticate(username=username, password=password)       # 然后再进行验证
                if user:    # 如果用户名存在
                    self.cleaned_data["user"] = user   # 那么返回用户名
                    return self.cleaned_data
            raise forms.ValidationError("用户名或者密码错误")
        else:
            self.cleaned_data["user"] = user    # 如果没有问题，那么返回一个验证成功的对象
        return self.cleaned_data        # 如果没有问题，那么返回一个方法


class RegForm(forms.Form):
    username = forms.CharField(label="用户名",
                               min_length=3,
                               max_length=30,
                               widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "请输入用户名"}))
    email = forms.EmailField(label="邮箱",
                             widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "请输入邮箱"}))

    verification_code = forms.CharField(label="验证码",
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "点击'发送验证码'，发送到邮箱"}))

    password = forms.CharField(label="密码",
                               min_length=6,
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入密码"}))
    password_again = forms.CharField(label="再输入一次密码",
                                     min_length=6,
                                     widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请再次输入密码"}))
    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        # 验证验证码是否正确
        code = self.request.session.get("register_code", "")  # 取出缓存中生成的验证码
        verification_code = self.cleaned_data.get("verification_code", "")  # 取出用户输入的验证码

        if not (code == verification_code and code != ""):
            raise forms.ValidationError("验证码不正确！")
        return self.cleaned_data
    def clean_verification_code(self):  # 验证  验证码是否为空
        verification_code = self.cleaned_data.get("verification_code", "").strip()
        if verification_code == "":
            raise forms.ValidationError("验证码不能为空")
        return verification_code

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已存在")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱已存在")
        return email

    def clean_password_again(self):
        password = self.cleaned_data["password"]
        password_again = self.cleaned_data["password_again"]
        if password != password_again:
            raise forms.ValidationError("两次密码不一致")
        return password_again


class ChangePassWord(forms.Form):   # 密码修改表单
    old_password = forms.CharField(label="旧的密码",
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入旧的密码"}))
    new_password = forms.CharField(label="新的密码",
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入新的密码"}))
    new_password_again = forms.CharField(label="再次输入新的密码",
                               widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "再次输入新的密码"}))

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):
        new_password = self.cleaned_data.get("new_password", "")
        new_password_again = self.cleaned_data.get("new_password_again", "")
        if new_password != new_password_again or new_password == "":
            raise forms.ValidationError("两次输入密码不一致")
        return self.cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password", "")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("旧密码不正确")
        return old_password


class ForgotPassword(forms.Form):
    email = forms.EmailField(label="邮箱",
                             widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "请输入绑定邮箱"}))

    verification_code = forms.CharField(label="验证码",
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "点击'发送验证码'，发送到邮箱"}))
    new_password = forms.CharField(label="新密码",
                                   widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入新的密码"}))

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("邮箱不存在")
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get("verification_code", "").strip()
        if verification_code == "":
            raise forms.ValidationError("验证码不能为空")

        code = self.request.session.get("forgot_password_code", "")  # 取出缓存中生成的验证码
        verification_code = self.cleaned_data.get("verification_code", "")  # 取出用户输入的验证码
        if not (code == verification_code and code != ""):
            raise forms.ValidationError("验证码不正确！")

        return verification_code




