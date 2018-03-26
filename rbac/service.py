#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
from django.conf import settings

from . import models


def initial_permission(request, user_id):
    """
    初始化权限，获取当前用户权限并添加到session中
    将当前用户权限信息转换为以下格式，并将其添加到Session中
        {
            '/index.html': ['GET','POST','DEL','EDIT],
            '/detail-(\d+).html': ['GET','POST','DEL','EDIT],
        }
    
    :param request: 请求对象
    :param user_id: 当前用户id
    :return: 
    """

    """初始化权限信息"""
    roles = models.Role.objects.filter(users__user_id=user_id)

    p2a = models.Permission2Action2Role.objects.filter(role__in=roles).values('permission__url',
                                                                              "action__code").distinct()
    user_permission_dict = {}
    for item in p2a:
        if item['permission__url'] in user_permission_dict:
            user_permission_dict[item['permission__url']].append(item['action__code'])
        else:
            user_permission_dict[item['permission__url']] = [item['action__code'], ]

    request.session[settings.RBAC_PERMISSION_SESSION_KEY] = user_permission_dict

    """初始化菜单信息，将菜单信息和权限信息添加到session中"""
    menu_list = list(models.Menu.objects.values('id', 'caption', 'parent_id'))

    menu_permission_list = list(models.Permission2Action2Role.objects.filter(role__in=roles,
                                                                        permission__menu__isnull=False).values(
        'permission_id',
        'permission__url',
        'permission__caption',
        'permission__menu_id').distinct())
    request.session[settings.RBAC_MENU_PERMISSION_SESSION_KEY] = {
        settings.RBAC_MENU_KEY: menu_list,
        settings.RBAC_MENU_PERMISSION_KEY: menu_permission_list
    }


def fetch_permission_code(request, url):
    """
    根据URL获取该URL拥有的权限，如：["GET","POST"]
    :param request: 
    :param url: 
    :return: 
    """
    user_permission_dict = request.session.get(settings.RBAC_PERMISSION_SESSION_KEY)
    if not user_permission_dict:
        return []
    for pattern, code_list in user_permission_dict.items():
        if re.match(pattern, url):
            return code_list
    return []
