#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
用于Django视图CBV模式时，根据请求地址后携带md对应的值执行相应的方法，如:
from django.views import View
class MyView(RbacView,View):
    def get(request, *args, **kwargs):
        pass
    
    def delete(request, *args, **kwargs):
        pass
        
    def put(request, *args, **kwargs):
        pass
    
    def delete(request, *args, **kwargs):
        pass
    
    MyView类中方法的名称取决于数据库action表code字段的值。PS:此处方法为小写
"""

class RbacView(object):
    def dispatch(self, request, *args, **kwargs):
        permission_code = request.permission_code.lower()
        handler = getattr(self, permission_code)
        return handler(request, *args, **kwargs)
