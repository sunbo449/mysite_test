import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail
from blog.models import Blog, BlogType

# 创建一个通用的方法
def read_statistics_once_read(request, obj):        # 需要传递request和一个对象的名称
    ct = ContentType.objects.get_for_model(obj)     # 使用  ContentType 获取该对象的模型类的名称
    key = "%s_%s_read" % (ct.model, obj.pk)     # 将模型类（在这里是字符串类型）和该实例对象的id关联起来，创建一个主键
    # 在浏览器Cookie中存储的形式就是 ： blog_4_read   类名(自己设置的)_主键值_自己设置的标识
    if not request.COOKIES.get(key):        # 然后查询浏览器的Cookie中是否存在这个key
        # if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
        #     # 如果筛选出，有这条阅读记录，那么取出这篇博客，阅读量加1
        #     readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        #     print("readnum:", readnum)
        # # 如果不存在阅读记录，那么创建这篇博客的实例化对象，并将其对应的阅读记录，加1并保存记录
        # else:
        #     readnum = ReadNum(content_type=ct, object_id=obj.pk)
        # 使用django中提供的简便方法：（阅读总数量）
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        # if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk, date=timezone.now().date()):
        #     readDetael = ReadDetail.objects.get(content_type=ct, object_id=obj.pk, date=timezone.now().date())
        # else:
        #     readDetael = ReadDetail(content_type=ct, object_id=obj.pk, date=timezone.now().date())
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=timezone.now().date())
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_read_data(content_type):     # 获取前七天的阅读量
    today = timezone.now().date()
    # today - datetime.timedelta(days=1)    获取的值是今天减去前一天，就是昨天。timedelta是时间差值方法
    dates = []
    read_nums = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime("%m/%d"))
        read_datails = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_datails.aggregate(read_num_sum=Sum("read_num"))
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums

def get_today_hot_data(content_type):   # 对当天博客的阅读量进行排序（倒叙）
    today = timezone.now().date()   # 获取当天的时间
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by("-read_num")  # 获取当天的所有博客数据查询集，并且对查询集的read_num字段进行倒叙排序
    return read_details[:7]     # 如果想要显示前几条，可以使用切片返回，这样就可以筛选出前几条数据

def get_yesterday_hot_data(content_type):   # 对昨天的博客阅读量进行倒叙排序
    today = timezone.now().date()   # 获取当天的时间
    yesterday = today - datetime.timedelta(days=1)  # 获取昨天的日期
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by("-read_num")  # 获取当天的所有博客数据查询集，并且对查询集的read_num字段进行倒叙排序
    return read_details[:7]

# def get_7_hot_data(content_type):  # 对本周内的博客阅读量进行倒叙排序，这是一个时间段内的数据，所以要获得一个时间段
#     today = timezone.now().date()  # 获取当天的时间
#     data = today - datetime.timedelta(days=7)      # 获取7天前的时间
#     read_details = ReadDetail.objects.filter(content_type=content_type, date__lt=today, date__gte=data)\
#                                      .values("content_type", "object_id")\
#                                      .annotate(read_sum_num=Sum("read_num"))\
#                                      .order_by("-read_sum_num")
#     return read_details[:7]

def get_7_days_hot_blogs():     # 本周内的博客阅读量进行统计
    today = timezone.now().date()  # 获取当天的时间
    date = today - datetime.timedelta(days=7)  # 获取7天前的时间
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)\
                        .values("id", "title")\
                        .annotate(read_num_sum=Sum("read_details__read_num"))\
                        .order_by("-read_num_sum")
    return blogs[:7]

def get_30_days_hot_blogs():     # 本30天内的的博客阅读量进行统计
    today = timezone.now().date()  # 获取当天的时间
    date = today - datetime.timedelta(days=31)  # 获取7天前的时间
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)\
                        .values("id", "title")\
                        .annotate(read_num_sum=Sum("read_details__read_num"))\
                        .order_by("-read_num_sum")
    return blogs[:7]


