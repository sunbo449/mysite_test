from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from read_statistics.utils import get_seven_days_read_data
from blog.models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read, get_today_hot_data, get_yesterday_hot_data,\
                                  get_7_days_hot_blogs,get_30_days_hot_blogs
from mysite.forms import LoginForm


def home(request):   # 首页
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)

    # 设置数据库缓存(获取7天热门博客数据缓存)
    hot_blogs_7_days = cache.get("hot_blogs_7_days", )
    # if hot_blogs_7_days is None:
    #     hot_blogs_7_days = get_7_days_hot_blogs()
    #     cache.set("hot_blogs_7_days", hot_blogs_7_days, 5)
    #     print("计算")
    # else:
    #     print("使用")

    cache.get_or_set("hot_blogs_7_days", hot_blogs_7_days, 5)

    context = {}
    context["read_nums"] = read_nums
    context["dates"] = dates
    context["today_hot_data"] = get_today_hot_data(blog_content_type)
    context["yesterday_hot_data"] = get_yesterday_hot_data(blog_content_type)
    context["hot_blogs_7_days"] = get_7_days_hot_blogs()
    context["hot_blogs_30_days"] = get_30_days_hot_blogs()
    return render(request, "home.html", context)

def get_blog_list_common_data(request, blog_all_list):   # 所有函数共用的函数方法
    paginator = Paginator(blog_all_list, settings.BLOG_NUMBER)  # 导入分页器进行分页,每3篇分为一页
    page_num = request.GET.get("page", "1")  # 获取用户request的页码
    page_of_blogs = paginator.get_page(page_num)  # 获取页面并且返回每页博客的数量

    # 博客分页优化(需求：只显示当前页码的前两页和后两页，以及最前最后页码)
    currentr_page_num = page_of_blogs.number  # 获取当前页码
    # 获取当前页码的前后两个的页码
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, "...")
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append("...")
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # # 获取博客分类中每个分类的对应博客数量
    # 第一种方法
    # blog_types = BlogType.objects.all()   # 1、获取所有的类型的查询集
    # blog_types_list = []
    # for blog_type in blog_types:    # 2、遍历该类型的所有博客的查询集
    #     # 3、筛选获取该查询集的个数，并且给该返回值设置一个方法
    #     blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
    #     blog_types_list.append(blog_type)   # 4、将返回值添加到一个列表中

    # 按照日期给博客进行归类
    blog_dates = Blog.objects.dates("created_time", "day", order="DESC")     # 1、获取创建时间的字段
    blog_dates_dict = {}    # 2、创建一个空的字典来进行传递参数
    for blog_date in blog_dates:       # 3、遍历获取每一条的统计日期
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,     # 4、筛选出对应的博客数量
                                         created_time__month=blog_date.month,
                                         created_time__day=blog_date.day).count()
        # 5、将对应的博客数量和对应的日期利用字典的键值对关系，进行对应。日期对应数量，传递给模板
        blog_dates_dict[blog_date] = blog_count
    context = {}
    context["page_range"] = page_range
    context["blogs"] = page_of_blogs.object_list
    context["page_of_blogs"] = page_of_blogs  # 将返回每页的博客数量赋值给context
    # context["blog_types"] = blog_types_list       # 5、将这个列表返回传递给模板文件
    # 第二种方法统计对应分类的博客数量
    context["blog_types"] = BlogType.objects.annotate(blog_count=Count("blog"))

    context["blog_dates"] = blog_dates_dict   # 6、将日期博客归纳传递给模板
    return context

def blog_list(request):     # 博客列表页面
    blog_all_list = Blog.objects.all()      # 获取博客列表全部数据
    context = get_blog_list_common_data(request, blog_all_list)
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, blog_pk):  # 博客详情
    blog = get_object_or_404(Blog, pk=blog_pk)      # 取出对应的blog_pk中的Blog查询集
    read_cookie_key = read_statistics_once_read(request, blog)

    context = {}
    context["previous_blog"] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context["next_blog"] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context["blog"] = blog
    context["login_form"] = LoginForm()
    response = render(request, "blog/blog_detail.html", context)
    response.set_cookie(read_cookie_key, "true")
    return response

def blogs_with_type(request, blog_type_pk):  # 博客分类
    blog_type = get_list_or_404(BlogType, pk=blog_type_pk)
    blog_all_list = Blog.objects.filter(blog_type=blog_type_pk)  # 获取博客列表全部数据
    context = get_blog_list_common_data(request, blog_all_list)
    context["blog_type"] = blog_type
    return render(request, "blog/blgos_with_type.html", context)


def blogs_with_date(request, year, month, day):
    # 按照时间筛选出信息
    blog_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month, created_time__day=day)  # 获取指定的年月分的博客数据
    context = get_blog_list_common_data(request, blog_all_list)
    context["blogs_with_date"] = "%s年%s月%s日" % (year, month, day)
    return render(request, 'blog/blogs_with_date.html', context)


