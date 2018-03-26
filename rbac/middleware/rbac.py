#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse


class RbacMiddleware(MiddlewareMixin):
    def process_request(self, request, *args, **kwargs):
        """
        检查用户是否具有权限访问当前URL
        :param request: 
        :param args: 
        :param kwargs: 
        :return: 
        """

        """跳过无需权限访问的URL"""
        for pattern in settings.RBAC_NO_AUTH_URL:
            if re.match(pattern, request.path_info):
                return None

        """获取当前用户session中的权限信息"""
        permission_dict = request.session.get(settings.RBAC_PERMISSION_SESSION_KEY)
        if not permission_dict:
            return HttpResponse(settings.RBAC_PERMISSION_MSG)

        """当前URL和session中的权限进行匹配"""

        flag = False
        for pattern, code_list in permission_dict.items():
            upper_code_list = [item.upper() for item in code_list]
            if re.match(pattern, request.path_info):
                request_permission_code = request.GET.get(settings.RBAC_QUERY_KEY, settings.RBAC_DEFAULT_QUERY_VALUE).upper()
                if request_permission_code in upper_code_list:
                    request.permission_code = request_permission_code
                    request.permission_code_list = upper_code_list
                    flag = True
                    break

        if not flag:
            return HttpResponse(settings.RBAC_PERMISSION_MSG)
