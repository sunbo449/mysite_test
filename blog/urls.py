from django.urls import path
from django.conf.urls import url
from blog import views

app_name = "blog"
urlpatterns = [
    url(r"^type/(?P<blog_type_pk>[0-9]+)$", views.blogs_with_type, name="blogs_with_type"),
    path(r"<int:blog_pk>", views.blog_detail, name="blog_detail"),
    url(r"blog_list/", views.blog_list, name="blog_list"),
    path(r"date/<int:year>/<int:month>/<int:day>", views.blogs_with_date, name="blogs_with_date"),
    path("", views.home, name="home"),

]
