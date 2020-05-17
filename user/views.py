import string
import random
import time
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from .forms import ChangeNickForm, BinEmailForm
from mysite.forms import ChangePassWord, ForgotPassword
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Profile

def change_nick_name(request):
    redirect_to = request.GET.get("from", reverse("blog:home"))
    if request.method == "POST":        #
        form = ChangeNickForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data["nickname_new"]
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNickForm()

    context = {}
    context["page_title"] = "修改昵称"
    context["form_title"] = "修改昵称"
    context["submit_text"] = "修改"
    context["form"] = form
    context['return_back_url'] = redirect_to

    return render(request, "forms.html", context)


def bind_email(request):
    redirect_to = request.GET.get("from", reverse("blog:home"))
    if request.method == "POST":
        form = BinEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data["email"]
            request.user.email = email
            request.user.save()
            # 清除Session
            del request.session["bind_email_code"]
            return redirect(redirect_to)
    else:
        form = BinEmailForm()

    context = {}
    context["page_title"] = "绑定邮箱"
    context["form_title"] = "绑定邮箱"
    context["submit_text"] = "绑定"
    context["form"] = form
    context['return_back_url'] = redirect_to

    return render(request, "bind_email.html", context)

def send_verification_code(request):
    email = request.GET.get("email", "")
    data = {}
    send_for = request.GET.get("send_for", "")
    if email != "":
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        request.session["bind_email_code"] = code
        now = int(time.time())
        send_code_time = request.session.get("send_code_time", 0)
        if now - send_code_time < 30:
            data["status"] = "ERROR"
            # 发送邮件
        else:
            request.session[send_for] = code
            request.session["send_code_time"] = now

            send_mail(
                "绑定邮箱",
                "验证码：%s" % code,
                "309593135@qq.com",
                [email],
                fail_silently=False,
            )
            data["status"] = "SUCCESS"
    else:
        data["status"] = "ERROR"
    return JsonResponse(data)


def change_password(request):
    redirect_to = reverse("blog:home")
    if request.method == "POST":  #
        form = ChangePassWord(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data["new_password"]
            user.set_password(new_password)
            user.save()
            logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePassWord()

    context = {}
    context["page_title"] = "修改密码"
    context["form_title"] = "修改密码"
    context["submit_text"] = "修改"
    context["form"] = form
    context['return_back_url'] = redirect_to

    return render(request, "forms.html", context)


def forgot_password(request):
    redirect_to = reverse("comment:blog_login")
    if request.method == "POST":
        form = ForgotPassword(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data["email"]
            new_password = form.cleaned_data["new_password"]
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除Session
            del request.session["forgot_password_code"]
            return redirect(redirect_to)
    else:
        form = ForgotPassword()

    context = {}
    context["page_title"] = "重置密码"
    context["form_title"] = "重置密码"
    context["submit_text"] = "重置"
    context["form"] = form
    context['return_back_url'] = redirect_to

    return render(request, "forgot_password.html", context)





