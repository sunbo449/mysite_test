from django.urls import path
from comment import views

app_name = "comment"
urlpatterns = [
    path("blog_login", views.blog_login, name="blog_login"),    # 评论框，登陆页面
    path("update_comment", views.update_comment, name="update_comment"),    # 评论提交处理
    path("register", views.register, name="register"),  # 注册页面
    path("login_for_model", views.login_for_model, name="login_for_model"),   # 注册登陆框提交处理
]


