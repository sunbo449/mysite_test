from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path("change_nick_name", views.change_nick_name, name="change_nick_name"),
    path("bind_email", views.bind_email, name="bind_email"),
    path("send_verification_code", views.send_verification_code, name="send_verification_code"),
    path("change_password", views.change_password, name="change_password"),
    path("forgot_password", views.forgot_password, name="forgot_password"),
]


