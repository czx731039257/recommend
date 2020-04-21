from django.utils.deprecation import MiddlewareMixin
# from django.http import HttpResponse
from django.shortcuts import HttpResponse, redirect,HttpResponseRedirect
import re
from django.http import JsonResponse
from rmsystem import models
# 方式一：
class MyMiddleware(MiddlewareMixin):


    def process_request(self, request):
        self.list_white=['/login','/layout','/verify','error']
        url = request.path_info
        url = re.match('^/[a-zA-Z]*_*[a-zA-Z]*_*[a-zA-Z]*', url).group()
        print('路径:', url)

        if self.list_white.__contains__(url):
            return None
        permissions=models.Permission.objects.all()
        allpermissions=[]
        for permission in permissions:
            allpermissions.append(permission.url)
        permissions=request.session.get('permissions')
        if permissions is None:
            return HttpResponseRedirect('/login',{'msg':'success'})
        if url in allpermissions:
            if not permissions.__contains__(url):
                if not list(url).__contains__('_'):
                    return HttpResponseRedirect('/error')
                else:
                    return JsonResponse({'msg':'nopermission'})
        return None




    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_exception(self, request, exception):
        if isinstance(exception, ValueError):
            return HttpResponse("404")

    def process_response(self, request, response):
        return response
