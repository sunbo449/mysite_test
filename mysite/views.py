
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import logout

def blog_logout(request):
    logout(request)
    return redirect(request.GET.get("from", reverse("blog:home")))     # 否则返回登陆前的页面或者首页

def user_info(request):
    context = {}
    return render(request, 'user_info.html', context)


