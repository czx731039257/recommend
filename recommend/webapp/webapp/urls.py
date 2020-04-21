"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path
from rmsystem import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [

    #基本url
    path('index', views.index),
    path('login',views.login),
    path('layout',views.layout),
    path('verify',views.verify),
    path('error',views.error),

    #调试用的url
    path('initUserData/', views.initUserData),
    path('initMovieData/', views.initMovieData),
    path('initMovieGenres/',views.initMovieGenres),
    path('initcluster/',views.initcluster),
    path('initUserCluster/',views.initUserCluster),
    path('compute_cluster/', views.compute_cluster),

    #热度榜相关url
    path('heat',views.heat), #获取热度榜页面
    url('get_heat/?',views.get_heat), #查看热度榜

    #个性化推荐相关的url
    path('recommend',views.recommend), #获取个性化推荐页面
    url('get_recommend/?',views.get_recommend), #查看推荐结果

    #收藏夹相关url
    path('collection',views.collection), #获取收藏夹页面
    url('del_collection/?',views.del_collection), #删除收藏
    url('get_collection/?',views.get_collection), #查看收藏
    url('add_collection/?',views.add_collection), #添加收藏



    #修改密码相关的url
    path('password',views.password), #获取修改页面
    url('edit_password/?',views.edit_password), #修改密码

    #电影相关的url
    path('allmovies', views.allmovies),  # 获取电影信息管理页面
    url('get_allmovies/?',views.get_allmovies), #查看电影信息
    url('movieDetail/?',views.movieDetail), #获取电影介绍页面

    #权限相关的url
    path('allpermissions',views.allpermissions), #获取权限页面
    url('get_allpermissions/?',views.get_allpermissions), #查看权限
    url('del_permission/?',views.del_permission), #删除权限
    url('addpermission/?',views.addpermission), #获取添加权限页面
    url('add_permission/?',views.add_permission), #添加权限
    url('editpermission/?',views.editpermission), #获取编辑权限页面
    url('edit_permission/?',views.edit_permission), #修改权限
    url('get_allpermission/?',views.get_allpermission),

    #角色相关的url
    path('allroles',views.allroles), #获取角色页面
    url('get_allroles/?',views.get_allroles), #查看角色
    url('del_role/?',views.del_role), #删除角色
    path('addrole',views.addrole), #获取添加角色页面
    url('add_role/?',views.add_role), #添加角色
    path('editrole',views.editrole), #获取修改角色页面
    url('edit_role/?',views.edit_role), #修改角色

    url('get_x/?',views.get_x),

    #用户信息相关的url
    path('userinfo',views.userinfo), #获取用户信息页面
    url('edit_userinfo/?',views.edit_userinfo), #修改用户信息
    url('get_userinfo/?',views.get_userinfo), #查看用户信息
    url('get_userhasrole/?',views.get_userhasrole),
    path('personinfo', views.personinfo),  # 获取个人信息页面
    url('get_personinfo/?', views.get_personinfo),  # 查看个人信息
    url('edit_personinfo/?', views.edit_personinfo), # 编辑个人信息
    path('allusers', views.allusers),  # 获取所有用户信息管理页面
    url('get_allusers/?', views.get_allusers),  # 查看用户信息
    path('edituser',views.edituser), #获取编辑用户页面
    url('update_head/?',views.update_head), #修改头像
    path('allrecords',views.allrecords),
    url('get_allrecords/?',views.get_allrecords),
    url('clear_records/?',views.clear_records)


] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
