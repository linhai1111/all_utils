from django.shortcuts import render
from django.shortcuts import redirect
from app01 import models
from rbac.service import initial_permission
from django.shortcuts import HttpResponse
import datetime
import json


# Create your views here.
def login(request):
    """
    用户登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        obj = models.UserInfo.objects.filter(user__username=username, user__password=password).first()
        if obj:
            # 登陆成功后，将用户信息保存到session当中
            request.session['user_info'] = {'username': username, 'nickname': obj.nickname, 'nid': obj.id}
            initial_permission(request, obj.user_id)  # 初始化用户对应的权限
            return redirect('/index.html')
        else:
            return render(request, 'login.html')


def index(request):
    """
    显示首页
    :param request:
    :return:
    """
    if not request.session['user_info']:
        return redirect('/login.html')
    return render(request, 'index.html')


def problem(request):
    """
    报障功能
    :param request:
    :return:
    """
    if request.permission_code == 'LOOK':  # 该值在中间件已经处理成request字典中的一个值
        problem_list = models.Order.objects.filter(create_user_id=request.session['user_info']['nid'])
        return render(request, 'problem.html', {'problem_list': problem_list})
    elif request.permission_code == 'DEL':
        nid = request.GET.get('nid')
        models.Order.objects.filter(create_user_id=request.session['user_info']['nid'], id=nid).delete()
        return redirect('/problem.html')
    elif request.permission_code == 'POST':
        if request.method == 'GET':
            return render(request, 'problem_add.html')
        else:
            title = request.POST.get('title')
            content = request.POST.get('content')
            models.Order.objects.create(title=title, detail=content, create_user_id=request.session['user_info']['nid'])
            return redirect('/problem.html')


def problem_kill(request):
    """
    处理报障单
    :param request:
    :return:
    """
    nid = request.session['user_info']['nid']  # 获得登陆用户的Id
    if request.permission_code == 'LOOK':
        # 查看列表，未解决,当前用户已经解决或正在解决
        from django.db.models import Q
        problem_list = models.Order.objects.filter(Q(status=1) | Q(processor_id=nid)).order_by('status')
        return render(request, 'problem_kill_look.html', {'problem_list': problem_list})

    elif request.permission_code == 'EDIT':
        # http://127.0.0.1:8000/trouble-kill.html?md=edit&nid=1
        if request.method == 'GET':  # 跳转到处理页面
            order_id = request.GET.get('nid')
            # 用户已经抢到过，处于处理中状态
            if models.Order.objects.filter(id=order_id, processor_id=nid, status=2):
                obj = models.Order.objects.filter(id=order_id).first()
                return render(request, 'problem_kill_edit.html', {'obj': obj})
            # 没有人抢到过,处于未处理状态，
            res = models.Order.objects.filter(id=order_id, status=1).update(processor_id=nid, status=2)
            if not res:
                return HttpResponse("已经有人在处理了")
            else:
                obj = models.Order.objects.filter(id=order_id).first()
                return render(request, 'problem_kill_edit.html', {'obj': obj})
        else:
            order_id = request.GET.get('nid')
            solution = request.POST.get('solution')
            models.Order.objects.filter(id=order_id, processor_id=nid).update(solution=solution, status=3,
                                                                              ptime=datetime.datetime.now())
            return redirect('/problem_kill.html')

def report(request):
    if request.permission_code == 'LOOK':   # 用户权限操作为LOOK时
        if request.method == 'GET':
            return render(request, 'report.html')
        else:
            from django.db.models import Count
            # 组装饼图所需要的数据格式
            result = models.Order.objects.filter(status=3).values_list('processor__nickname').annotate(ct=Count('id'))
            # 分组：select * from xx group by processor_id,ptime(2017-11-11)
            # 折线图
            # strftime('%%s',strftime('%%Y-%%m-%%d',ptime)) 表示将2017-02-03 12：30：20转换成2017-02-03，再转换成折线图所需要的时间戳格式
            ymd_list = models.Order.objects.filter(status=3).extra(select={'ymd':"strftime('%%s',strftime('%%Y-%%m-%%d',ptime))"}).values('processor_id','processor__nickname','ymd').annotate(ct=Count('id'))
            ymd_dict = {}
            for row in ymd_list:
                key = row['processor_id']
                if key in ymd_dict:
                    ymd_dict[key]['data'].append(float(row['ymd']*1000),row['ct'])
                else:
                    # 折线图需要*1000的数据
                    ymd_dict[key] = {'name':row['processor__nickname'],'data':[[float(row['ymd'])*1000, row['ct']], ]}
            response={
                'zhexian': list(ymd_dict.values()),
                'pie': [['方少伟', 45.0], ['吴永强', 40.0], ['友情并', 3], ['尹树林', 90]],
            }
            return HttpResponse(json.dumps(response))