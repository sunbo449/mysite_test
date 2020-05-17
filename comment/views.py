from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse

from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import Comment
from .forms import CommentForm
from mysite.forms import LoginForm, RegForm

def blog_login(request):    # 登陆处理
    if request.method == "POST":
        login_form = LoginForm(request.POST)  # 点击提交用户名密码后，处理函数获取到login_form实例对象
        if login_form.is_valid():   # 判断数据是否合法，如果合法
            user = login_form.cleaned_data["user"]      # 获取实例对象中的cleaned_date的方法返回的验证后的user
            login(request, user)    # 执行登陆操作
            return redirect(request.GET.get("from", reverse("blog:home")))  # 否则返回登陆前的页面或者首页
    else:   # 如果不是通过 post 访问的页面，那么就创建一个空的对象，返回到前端页面
        login_form = LoginForm()

    context = {}
    context["login_form"] = login_form
    return render(request, "login.html", context)

def login_for_model(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():  # 判断数据是否合法，如果合法
        user = login_form.cleaned_data["user"]  # 获取实例对象中的cleaned_date的方法返回的验证后的user
        login(request, user)  # 执行登陆操作
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def register(request):
    if request.method == "POST":
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data["username"]
            email = reg_form.cleaned_data["email"]
            password = reg_form.cleaned_data["password"]
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 清除session，避免出现重复注册
            del request.session["register_code"]
            # 登录用户
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(request.GET.get("from", reverse("blog:home")))
    else:
        reg_form = RegForm()

    context = {}
    context["reg_form"] = reg_form
    return render(request, "register.html", context)


def update_comment(request):    # 评论提交处理，通用方法，评论什么都可以引用这个方法
    referer = request.META.get("HTTP_REFERER", reverse("blog:home"))  # 获取当前页面信息，如果没有获取首页
    comment_form = CommentForm(request.POST, user=request.user)   # 实例化评论提交表单对象
    data = {}

    if comment_form.is_valid():     # 如果提交的数据合法
        comment = Comment()  # 创建一个评论模型的实例对象
        comment.user = comment_form.cleaned_data["user"]    # 获取到user用户名字段
        comment.text = comment_form.cleaned_data["text"]     # 获取到评论信息字段
        comment.content_object = comment_form.cleaned_data["content_object"]     # 获取到具体的对象

        parent = comment_form.cleaned_data["parent"]   # 先获取parent
        if parent:  # 判断是否为none，如果不是那么就不是顶级评论，而是回复。我们就进行处理。
            comment.root = parent.root if parent.root else parent    # 判断parent是是否为none，如果不是那么取出来root就是回复
            comment.parent = parent
            comment.reply_to = parent.user  # 评论的谁  
            # 保存这个实例对象
        comment.save()

        # 发送邮件通知
        comment.send_mail()

        # 返回数据
        data["status"] = "SUCCESS"
        data["username"] = comment.user.username
        data["comment_time"] = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S")
        data["text"] = comment.text

        if parent:   # 如果是回复的
            data["reply_to"] = comment.reply_to.username # 那么我们获取到回复给的谁
        else:
            data["reply_to"] = ""    # 如果不是那么返回空就可以
        data["pk"] = comment.pk
        data["root_pk"] = comment.root.pk if comment.root else ""

    else:
        data["status"] = "ERROR"
        data["message"] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)















