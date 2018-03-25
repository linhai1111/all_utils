import re
from rbac import models
from django.utils.safestring import mark_safe

def permission_session(user_id,request):
    """

    :param user_id:  rbac中的user表中一条数据id
    :param request:
    :return:
    """
    # obj = models.User.objects.filter(username='杨明').first()
    #
    # # x = models.User2Role.objects.filter(user_id=obj.id)
    # # [User2Role,User2Role,User2Role]
    #
    # role_list = models.Role.objects.filter(users__user_id=obj.id)
    # # [Role,]
    # from django.db.models import Count
    # # permission_list = models.Permission2Action2Role.objects.filter(role__in=role_list).values('permission__url','action__code').annotate(c=Count('id'))
    # permission_list = models.Permission2Action2Role.objects.filter(role__in=role_list).values('permission__url','action__code').distinct()
    """
    [
        {permission_url: '/index.html', action_code:'GET'},
        {permission_url: '/index.html', action_code:'POST'},
        {permission_url: '/index.html', action_code:'DEL'},
        {permission_url: '/index.html', action_code:'Edit'},
        {permission_url: '/order.html', action_code:'GET'},
        {permission_url: '/order.html', action_code:'POST'},
        {permission_url: '/order.html', action_code:'DEL'},
        {permission_url: '/order.html', action_code:'Edit'},
    ]
    放在Session中
    /index.html?md=GET

    {
        '/index.html': [GET,POST,DEL,Edit],
        '/order.html': [GET,POST,DEL,Edit],
    }

    """

    user_permission_dict = {
        '/ah-index.html': ["GET","POST","DEL","Edit"],
        '/order.html':  ["GET","POST","DEL","Edit"],
        '/index-(\d+).html':  ["GET","POST","DEL","Edit"],
    }

    request.session['user_permission_dict'] = user_permission_dict


def menu(user_id,current_url):
    """
    根据用户ID，当前URL:获取用户所有菜单以及权限，是否显示，是否打开
    :param user_id:
    :param current_url:
    :return:
    """
    # 所有菜单：处理成当前用关联的菜单
    all_menu_list = models.Menu.objects.all().values('id','caption','parent_id')
    user = models.User.objects.filter(id=user_id).first()
    role_list = models.Role.objects.filter(users__user=user)
    permission_list = models.Permission2Action2Role.objects.filter(role__in=role_list).values('permission__id','permission__url','permission__menu_id','permission__caption').distinct()
    ##### 将权限挂靠到菜单上 ########
    all_menu_dict = {}
    for row in all_menu_list:
        row['child'] = []      # 添加孩子
        row['status'] = False # 是否显示菜单
        row['opened'] = False # 是否默认打开
        all_menu_dict[row['id']] = row

    for per in permission_list:
        if not per['permission__menu_id']:
            continue

        item = {
            'id':per['permission__id'],
            'caption':per['permission__caption'],
            'parent_id':per['permission__menu_id'],
            'url': per['permission__url'],
            'status': True,
            'opened': False
        }
        if re.match(per['permission__url'],current_url):
            item['opened'] = True
        pid = item['parent_id']
        all_menu_dict[pid]['child'].append(item)

        # 将当前权限前辈status=True
        temp = pid # 1.父亲ID
        while not all_menu_dict[temp]['status']:
            all_menu_dict[temp]['status'] = True
            temp = all_menu_dict[temp]['parent_id']
            if not temp:
                break

        # 将当前权限前辈opened=True
        if item['opened']:
            temp1 = pid # 1.父亲ID
            while not all_menu_dict[temp1]['opened']:
                all_menu_dict[temp1]['opened'] = True
                temp1 = all_menu_dict[temp1]['parent_id']
                if not temp1:
                    break
    # ############ 处理菜单和菜单之间的等级关系 ############
    result = []
    for row in all_menu_list:
        pid = row['parent_id']
        if pid:
            all_menu_dict[pid]['child'].append(row)
        else:
            result.append(row)


    ##################### 结构化处理结果 #####################
    for row in result:
        print(row['caption'],row['status'],row['opened'],row)


    def menu_tree(menu_list):
        tpl1 = """
        <div class='menu-item'>
            <div class='menu-header'>{0}</div>
            <div class='menu-body {2}'>{1}</div>
        </div>
        """
        tpl2 = """
        <a href='{0}' class='{1}'>{2}</a>
        """

        menu_str = ""
        for menu in menu_list:
            if not menu['status']:
                continue
            # menu: 菜单，权限（url）
            if menu.get('url'):
                # 权限
                menu_str += tpl2.format(menu['url'],'active' if menu['opened'] else "",menu['caption'])
            else:
                # 菜单
                if menu['child']:
                    child_html = menu_tree(menu['child'])
                else:
                    child_html = ""
                menu_str += tpl1.format(menu['caption'], child_html,"" if menu['opened'] else 'hide')

        return menu_str
    menu_html = menu_tree(result)
    return menu_html


# simple_tag
def css():
    v = """
        <style>
        .hide{
            display: none;
        }
        .menu-body{
            margin-left: 20px;
        }
        .menu-body a{
            display: block;
        }
        .menu-body a.active{
            color: red;
        }
    </style>
        """
    return v

# simple_tag
def js():
    v = """
        <script>
        $(function(){

            $('.menu-header').click(function(){
                $(this).next().removeClass('hide').parent().siblings().find('.menu-body').addClass('hide');

            })

        })
    </script>
    """
    return mark_safe(v)