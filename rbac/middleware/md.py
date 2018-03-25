from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from rbac import config
import re


class RbacMiddleware(MiddlewareMixin):

    def process_request(self,request,*args,**kwargs):
        for pattern in config.VALID_URL:
            if re.match(pattern,request.path_info):
                return None

        action = request.GET.get('md') # GET
        user_permission_dict = request.session.get('user_permission_dict')
        if not user_permission_dict:
            return HttpResponse('无权限')

        # action_list = user_permission_dict.get(request.path_info)
        flag = False
        for k,v in user_permission_dict.items():
            if re.match(k,request.path_info):
                if action in v:
                    flag = True
                    break
        if not flag:
            return HttpResponse('无权限')
