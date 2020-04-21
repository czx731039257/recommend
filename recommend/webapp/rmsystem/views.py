from django.shortcuts import render,HttpResponseRedirect
from django.http import JsonResponse
from django.core.paginator import Paginator
import numpy as np
from rmsystem import models
import datetime
import time
import json
import pandas as pd
import math
import os
import uuid
from django.views.decorators.csrf import csrf_exempt

def isNone(a):
    if a !="" and not a is None:
        return False
    return True
def get_mat(A1,A2,A3,A4,A5,A6,A7,A8,A9,A10):
    list=[]
    list.append(json.loads(A1))
    list.append(json.loads(A2))
    list.append(json.loads(A3))
    list.append(json.loads(A4))
    list.append(json.loads(A5))
    list.append(json.loads(A6))
    list.append(json.loads(A7))
    list.append(json.loads(A8))
    list.append(json.loads(A9))
    list.append(json.loads(A10))
    return list



class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# Create your views here.
def index(request):
    return render(request,"rmsystem/index.html")


def initUserData(request):
    A = np.identity(10)
    b=np.zeros([10,1])
    AInv=np.linalg.inv(A)
    theta=np.dot(AInv,b)
    for i in range(500):
        A1=json.dumps(A[0].tolist())
        A2 = json.dumps(A[1].tolist())
        A3 = json.dumps(A[2].tolist())
        A4 = json.dumps(A[3].tolist())
        A5 = json.dumps(A[4].tolist())
        A6 = json.dumps(A[5].tolist())
        A7 = json.dumps(A[6].tolist())
        A8 = json.dumps(A[7].tolist())
        A9 = json.dumps(A[8].tolist())
        A10 = json.dumps(A[9].tolist())
        x=models.User.objects.create(id=i,password='123456',A1=A1,A2=A2,A3=A3,A4=A4,A5=A5,A6=A6,A7=A7,A8=A8,A9=A9,A10=A10,b=json.dumps(b.tolist()),theta=json.dumps(theta.tolist()))
        x.save()
    return render(request,"rmsystem/index.html")

def initMovieData(request):
    tag=pd.DataFrame(pd.read_csv('../ml-latest/cofiba/movie.csv'))
    len_tag=len(tag)
    i=0
    for index,row in tag.iterrows():
       print(i)
       i+=1
       movie=models.Movie.objects.create(id=row['movieId'],title=row['title'],genres=row['genres'],feature=row['feature'],click=0)
       movie.save()
    return render(request,"rmsystem/index.html")

def initMovieGenres(request):
    geners = models.Genres.objects.all()
    dict_genres={}
    for x in geners:
        dict_genres[x.name_en]=x.id
    movies=models.Movie.objects.all()
    name_en=dict_genres.keys()
    i=0
    for movie in movies:
        print(i)
        i+=1
        genr=movie.genres.strip().split('|')
        for g in genr:
            if name_en.__contains__(g):
                movie_genres=models.Movie_Genres.objects.create(Movie_id=movie.id,Genres_id=dict_genres[g])
                movie_genres.save()
    return render(request,"rmsystem/index.html")

def initcluster(request):
    I=np.identity(10).tolist()
    zero=np.zeros([10,1]).tolist()
    for i in range(280):
        cluster=models.Cluster.objects.create(
            id=i,
            A1=json.dumps(I[0]),
            A2=json.dumps(I[1]),
            A3=json.dumps(I[2]),
            A4=json.dumps(I[3]),
            A5=json.dumps(I[4]),
            A6=json.dumps(I[5]),
            A7=json.dumps(I[6]),
            A8=json.dumps(I[7]),
            A9=json.dumps(I[8]),
            A10=json.dumps(I[9]),
            b=json.dumps(zero),
            theta=json.dumps(zero)
        )
        cluster.save()

    return render(request,"rmsystem/index.html")

def initUserCluster(request):
    for i in range(500):
        models.User.objects.filter(id=i).update(Cluster_id=i%280)
    return render(request, "rmsystem/index.html")

def compute_cluster(request):
    I=np.identity(10)
    for i in range(280):
        users=models.User.objects.filter(Cluster_id=i)
        A=I
        b=np.zeros([10,1])
        for user in users:
            A+=(np.array(get_mat(user.A1,user.A2,user.A3,user.A4,user.A5,user.A6,user.A7,user.A8,user.A9,user.A10))-I)
            b+=json.loads(user.b)
        AInv=np.linalg.inv(A)
        theta = np.dot(AInv, b)
        A=A.tolist()
        b=b.tolist()
        models.Cluster.objects.filter(id=i).update(A1=A[0],A2=A[1],A3=A[2],A4=A[3],A5=A[4],A6=A[5],A7=A[6],A8=A[7],A9=A[8],A10=A[9],b=b,theta=theta)
        return render(request, "rmsystem/index.html")


def layout(request):
    request.session.flush()
    return HttpResponseRedirect('/login')

def error(request):
    return render(request,'rmsystem/error.html')

def allmovies(request):
    return render(request,'rmsystem/allmovies.html')

def get_allmovies(request):
    id = request.GET.get('id')
    title = request.GET.get('title')

    if isNone(id) == True and isNone(title) == False:
        movies = models.Movie.objects.filter(title__contains=title)
    elif isNone(id) == False and isNone(title) == True:
        movies = models.Movie.objects.filter(id=int(id))
    elif isNone(id) == True and isNone(title) == True:
        movies = models.Movie.objects.all()
    elif isNone(id) == False and isNone(title) == False:
        movies = models.Movie.objects.filter(id=int(id), title__contains=title)



    dataCount=movies.count()
    list=[]
    for movie in movies:
        dict={}
        dict['id']=movie.id
        dict['title']=movie.title
        dict['feature']=movie.feature
        dict['genres']=movie.genres
        dict['number_people']=movie.number_people
        list.append(dict)
    pageSize=request.GET.get('limit')
    pageIndex=request.GET.get('page')
    paginator = Paginator(list, pageSize)
    datas=paginator.page(pageIndex)
    res=[]
    for data in datas:
        res.append(data)
    contact={"code":0, "msg": "成功", "count":dataCount,"data":res}
    return JsonResponse(contact)

def allusers(request):
    return render(request,'rmsystem/allusers.html')

def get_allusers(request):
    id=request.GET.get('id')
    username=request.GET.get('username')
    if isNone(id)==True and isNone(username)==False:
        users = models.User.objects.filter(username__contains=username)
    elif isNone(id)==False and isNone(username)==True:
        users = models.User.objects.filter(id=int(id))
    elif isNone(id)==True and isNone(username)==True:
        users = models.User.objects.all()
    elif isNone(id)==False and isNone(username)==False:
        users = models.User.objects.filter(id=int(id),username__contains=username)

    dataCount=users.count()
    list=[]
    for user in users:
        dict={}
        dict['id']=user.id
        dict['username']=user.username
        dict['password']=user.password
        dict['sex']=user.sex
        dict['phone']=user.phone
        dict['email']=user.email
        dict['remarks']=user.remarks
        dict['rolename']=user.Role.name
        A=[]
        A.append(json.loads(user.A1))
        A.append(json.loads(user.A2))
        A.append(json.loads(user.A3))
        A.append(json.loads(user.A4))
        A.append(json.loads(user.A5))
        A.append(json.loads(user.A6))
        A.append(json.loads(user.A7))
        A.append(json.loads(user.A8))
        A.append(json.loads(user.A9))
        A.append(json.loads(user.A10))
        dict['A']=json.dumps(A)
        dict['b']=user.b
        dict['theta']=user.theta
        list.append(dict)

    pageIndex=request.GET.get('page')
    pageSize=request.GET.get('limit')
    paginator = Paginator(list, pageSize)
    datas=paginator.page(pageIndex)
    res=[]
    for data in datas:
        res.append(data)
    contact = {"code": 0, "msg": "成功", "count": dataCount, "data": res}
    return JsonResponse(contact)

def login(request):
    return render(request,'rmsystem/login.html')

def verify(request):
    username=request.POST.get('username')
    password=request.POST.get('password')
    user=models.User.objects.filter(id=int(username),password=password)
    count=user.count()
    if count == 1:
        request.session['userid']=user[0].id
        request.session['username'] = user[0].username
        request.session['head'] = user[0].head
        permissions=models.Role_Permission.objects.filter(Role_id=user[0].Role.id)
        permissionids=[]
        for permission in permissions:
            permissionids.append(permission.Permission.id)
        permissions=models.Permission.objects.filter(id__in=permissionids)
        urls=[]
        for permission in permissions:
            urls.append(permission.url)
        request.session['permissions']=urls
        return HttpResponseRedirect('/index',{'msg':'success'})
    return render(request,'rmsystem/login.html',{'msg':'false'})


def heat(request):
    return render(request,'rmsystem/heat.html')

def get_heat(request):
    userid=request.session.get('userid')
    allmovies=models.Movie.objects.all().order_by('-number_people')
    dataCount=allmovies.count()
    list={}
    for movie in allmovies:
        dict={}
        dict['id']=movie.id
        dict['title']=movie.title
        dict['genres']=movie.genres
        dict['number_people']=movie.number_people
        dict['collectState']='未收藏'
        list[movie.id]=dict
    collects = models.Collect.objects.filter(User_id=userid)
    for collect in collects:
        list[collect.Movie.id]['collectState'] = '已收藏'

    temp=[]
    for i in list.values():
        temp.append(i)
    pageSize=request.GET.get('limit')
    pageIndex=request.GET.get('page')
    paginator = Paginator(temp, pageSize)
    datas=paginator.page(pageIndex)
    res=[]
    for data in datas:
        res.append(data)
    contact={"code":0, "msg": "成功", "count":dataCount,"data":res}
    return JsonResponse(contact)

def edituser(request):
    id=request.POST.get('id')
    username=request.POST.get('username')
    password=request.POST.get('password')
    count = models.User.objects.filter(id=id).update(username=username, password=password)
    if count==1:
        contact={'msg':'success'}
    else:
        contact = {'msg': 'false'}
    return JsonResponse(contact)

def recommend(request):
    return render(request,'rmsystem/recommend.html')


def update_cluster(clusterid):
    I=np.identity(10)
    clusters=models.Cluster.objects.filter(id=clusterid)
    cluster=clusters[0]
    users=models.User.objects.filter(Cluster_id=cluster.id)
    A_cluster=np.array(get_mat(cluster.A1,cluster.A2,cluster.A3,cluster.A4,cluster.A5,cluster.A6,cluster.A7,cluster.A8,cluster.A9,cluster.A10))
    b_cluster=np.array(json.loads(cluster.b))
    for user in users:
        A_user=np.array(get_mat(user.A1,user.A2,user.A3,user.A4,user.A5,user.A6,user.A7,user.A8,user.A9,user.A10))
        A_cluster+=(A_user-I)
        b_cluster+=np.array(json.loads(user.b))
    theta_cluster=np.dot(np.linalg.inv(A_cluster),b_cluster)
    clusters.update(
        A1=json.dumps(A_cluster[0].tolist()),
        A2=json.dumps(A_cluster[1].tolist()),
        A3=json.dumps(A_cluster[2].tolist()),
        A4=json.dumps(A_cluster[3].tolist()),
        A5=json.dumps(A_cluster[4].tolist()),
        A6=json.dumps(A_cluster[5].tolist()),
        A7=json.dumps(A_cluster[6].tolist()),
        A8=json.dumps(A_cluster[7].tolist()),
        A9=json.dumps(A_cluster[8].tolist()),
        A10=json.dumps(A_cluster[9].tolist()),
        b=json.dumps(b_cluster.tolist()),
        theta=json.dumps(theta_cluster.tolist())
    )

def get_recommend(request):
    userid=request.session.get('userid')

    users=models.User.objects.filter(id=userid)
    user=users[0]
    old_clusterid=user.Cluster.id
    A_user=np.array(get_mat(user.A1,user.A2,user.A3,user.A4,user.A5,user.A6,user.A7,user.A8,user.A9,user.A10))
    b_user=np.array(json.loads(user.b))
    theta_user=np.dot(np.linalg.inv(A_user),b_user)
    clusters=models.Cluster.objects.all()
    min_value=-1
    new_cluster=clusters[0]
    for cluster in clusters:
        value = np.linalg.norm(np.array(json.loads(cluster.theta)) - theta_user)
        if value < min_value:
            min_value = value
            new_cluster = cluster
    if new_cluster.id!=old_clusterid:
        if len(models.User.objects.filter(Cluster_id=old_clusterid))>1:
            users.update(Cluster_id=new_cluster.id,theta=json.dumps(theta_user.tolist()))
            update_cluster(new_cluster.id)
            update_cluster(old_clusterid)
        else:
            users.update(theta=json.dumps(theta_user.tolist()))
            update_cluster(old_clusterid)
    else:
        users.update(theta=json.dumps(theta_user.tolist()))
        update_cluster(old_clusterid)



    likes=json.loads(request.GET.get('likes'))
    movieAndGenres = models.Movie_Genres.objects.filter(Genres__name_en__in=likes).values('Movie_id').distinct()

    movieids=set()
    for i in movieAndGenres:
        movieids.add(i['Movie_id'])
    allmovies = models.Movie.objects.filter(id__in=movieids)
    #allmovies=models.Movie.objects.all()
    list_allmovies= {}
    for movie in allmovies:
        dict = {}
        dict['id'] = movie.id
        dict['title'] = movie.title
        dict['feature'] = movie.feature
        dict['genres'] = movie.genres
        dict['number_people'] = movie.number_people
        dict['collectState']='未收藏'
        list_allmovies[movie.id]=dict

    set_hasRecommend=set()
    records=models.Record.objects.filter(User_id=userid)
    for record in records:
        set_hasRecommend.add(record.Movie.id)

    collects = models.Collect.objects.filter(User_id=userid)
    for collect in collects:
        set_hasRecommend.add(collect.Movie.id)

    new_movieids=movieids-set_hasRecommend
    temp={}
    for i in new_movieids:
        temp[i]=list_allmovies[i]
    list_allmovies=temp

    user = models.User.objects.filter(id=userid)[0]
    cluster=models.Cluster.objects.filter(id=user.Cluster_id)[0]
    scores ={}
    AInv = np.linalg.inv(np.array(get_mat(cluster.A1, cluster.A2, cluster.A3, cluster.A4, cluster.A5, cluster.A6, cluster.A7, cluster.A8,cluster.A9, cluster.A10)))
    mean = np.array(json.loads(cluster.theta)).T
    for id,movie in list_allmovies.items():
        x=np.array(json.loads(movie['feature']))

        var = math.sqrt(np.dot(np.dot(x.T,AInv), x))
        score = np.dot(mean, x)[0][0] + 0.2 * var
        scores[id]=score
    sorted_scores = sorted(scores.items(), key=lambda scores: scores[1], reverse=True)[0:10]
    res=[]

    for x in sorted_scores:
        res.append(list_allmovies[x[0]])

    #向推荐记录表中添加
    A = np.array(get_mat(user.A1, user.A2, user.A3, user.A4, user.A5, user.A6, user.A7, user.A8, user.A9, user.A10))
    for movie in res:
        x=json.loads(movie['feature'])
        A+=np.outer(x,x)
        rec=models.Record.objects.create(User_id=userid,Movie_id=movie['id'],click=0)
        rec.save()
    count=models.User.objects.filter(id=userid).update(
        A1=json.dumps(A[0].tolist()),
        A2=json.dumps(A[1].tolist()),
        A3=json.dumps(A[2].tolist()),
        A4=json.dumps(A[3].tolist()),
        A5=json.dumps(A[4].tolist()),
        A6=json.dumps(A[5].tolist()),
        A7=json.dumps(A[6].tolist()),
        A8=json.dumps(A[7].tolist()),
        A9=json.dumps(A[8].tolist()),
        A10=json.dumps(A[9].tolist())
    )

    contact = {"code":0,"msg":"成功","count":10,"data":res}
    return JsonResponse(contact)


def collection(request):
    return render(request, 'rmsystem/collection.html')


def get_collection(request):
    userid=request.session.get('userid')
    user_movies=models.Collect.objects.filter(User_id=userid)
    movies=[]
    for x in user_movies:
        movies.append(x.Movie_id)
    movies=models.Movie.objects.filter(id__in=movies)
    dataCount = movies.count()
    list = []
    for movie in movies:
        dict = {}
        dict['id'] = movie.id
        dict['title'] = movie.title
        dict['feature'] = movie.feature
        dict['genres'] = movie.genres
        dict['number_people'] = movie.number_people
        list.append(dict)
    pageSize = request.GET.get('limit')
    pageIndex = request.GET.get('page')
    paginator = Paginator(list, pageSize)
    datas = paginator.page(pageIndex)
    res = []
    for data in datas:
        res.append(data)
    contact = {"code": 0, "msg": "成功", "count": dataCount, "data": res}
    return JsonResponse(contact)

def del_collection(request):
    userid = request.session.get('userid')
    movieid= request.GET.get('movieid')
    operateType=request.GET.get('operateType')
    count=models.Collect.objects.filter(User_id=userid,Movie_id=movieid).delete()
    collects = models.Collect.objects.filter(Movie_id=movieid)
    number_people = len(collects)
    models.Movie.objects.filter(id=movieid).update(number_people=number_people)
    if operateType=='1':
        users=models.User.objects.filter(id=userid)
        b=np.array(json.loads(users[0].b))
        movies=models.Movie.objects.filter(id=movieid)
        x=np.array(json.loads(movies[0].feature))
        b=b-x
        users.update(b=json.dumps(b.tolist()))
        models.Record.objects.filter(User_id=userid, Movie_id=movieid).update(click=0)
    return JsonResponse({'number_people': number_people})


def add_collection(request):
    userid = request.session.get('userid')
    movieid = request.GET.get('movieid')
    operateType = request.GET.get('operateType')
    creat = models.Collect.objects.create(User_id=userid, Movie_id=movieid)
    collects=models.Collect.objects.filter(Movie_id=movieid)
    number_people=len(collects)
    models.Movie.objects.filter(id=movieid).update(number_people=number_people)
    if operateType == '1':
        users = models.User.objects.filter(id=userid)
        b = np.array(json.loads(users[0].b))
        movies = models.Movie.objects.filter(id=movieid)
        x = np.array(json.loads(movies[0].feature))
        b = b + x
        users.update(b=json.dumps(b.tolist()))
        models.Record.objects.filter(User_id=userid,Movie_id=movieid).update(click=1)
    return JsonResponse({'number_people': number_people})

def personinfo(request):
    return render(request, 'rmsystem/personinfo.html')

def get_personinfo(request):
    userid=request.session.get('userid')
    user=models.User.objects.filter(id=userid)
    userinfo={}
    userinfo['userid']=user[0].id
    userinfo['username'] = user[0].username
    userinfo['sex'] = user[0].sex
    userinfo['phone'] = user[0].phone
    userinfo['email'] = user[0].email
    userinfo['remarks'] = user[0].remarks
    userinfo['head'] = user[0].head
    userinfo['roleid']=user[0].Role.id
    request.session['head']=userinfo['head']
    print(request.session.get('head'))

    return JsonResponse(userinfo)

@csrf_exempt
def edit_personinfo(request):
    userid=request.GET.get('userid')
    username=request.GET.get('username')
    phone = request.GET.get('phone')
    sex = request.GET.get('sex')
    email = request.GET.get('email')
    remarks = request.GET.get('remarks')
    count=models.User.objects.filter(id=userid).update(username=username,sex=sex,phone=phone,email=email,remarks=remarks)
    if count==1:
        return JsonResponse({'msg':'success'})
    return JsonResponse({'msg':'fail'})

@csrf_exempt
def update_head(request):
    userid=request.POST.get('userid')
    img=request.FILES.get('file')
    img_type = os.path.splitext(img.name)[1]
    x=uuid.uuid1().__str__()
    new_path='D:\\pythonproject\\recommend\\webapp\\static\head\\'+x+img_type
    with open(new_path,'wb') as f:
        for line in img:
            f.write(line)
    users=models.User.objects.filter(id=int(userid))
    old_path='D:\\pythonproject\\recommend\\webapp'+users[0].head
    #print(old_path)
    if users[0].head!='/static/head/default.jpg':
        os.remove(old_path)
    users.update(head='/static/head/'+x+img_type)
    res={
        "code":0
        ,"msg":"success"
        ,"data":{
            "src":'/static/head/'+x+img_type
        }
    }
    print('/static/head/'+x+img_type)
    return JsonResponse(res)

def password(request):
    return render(request, 'rmsystem/password.html')


@csrf_exempt
def edit_password(request):
    userid = request.session.get('userid')
    currentpassword = request.GET.get('currentpassword')
    newpassword=request.GET.get('newpassword')
    user=models.User.objects.filter(id=userid)
    if(user[0].password!=currentpassword):
        return JsonResponse({'msg':'false'})
    models.User.objects.filter(id=userid).update(password=newpassword)
    res = {'msg': 'true'}
    return JsonResponse(res)

def list_to_str(list,startsep,midsep):
    out=startsep
    for i in range(len(list)):
        out+=list[i]
        if i!=len(list)-1:
            out+=midsep
    return out

def movieDetail(request):
    movieId = request.GET.get('movieId')
    file = open('D:\\pythonproject\\recommend\\ml-latest\\cofiba\\detail\\' + str(movieId) + '.text', 'r')
    text = json.loads(file.read())
    title = text['title']
    img = text['img']
    director = json.loads(text['director'])
    scriptwriter = json.loads(text['scriptwriter'])
    actor = json.loads(text['actor'])
    type = json.loads(text['type'])
    releasetime = json.loads(text['releasetime'])
    runtime = json.loads(text['runtime'])
    summary = json.loads(text['summary'])
    data = {}
    data['title'] = list_to_str(title,'',' / ')
    data['movieId'] = movieId
    data['director'] = list_to_str(director,'',' / ')
    data['scriptwriter'] = list_to_str(scriptwriter,'',' / ')
    data['actor'] = list_to_str(actor,'',' / ')
    data['type'] = list_to_str(type,'',' / ')
    data['releasetime']=list_to_str(releasetime,'',' / ')
    data['runtime'] = list_to_str(runtime,'',' / ')
    data['summary'] = summary
    return render(request, 'rmsystem/movieDetail.html',data)

def allpermissions(request):
    return render(request, 'rmsystem/allpermissions.html')

def get_allpermissions(request):
    name = request.GET.get('name')
    url=request.GET.get('url')
    if isNone(name) == True and isNone(url) == False:
        permissions = models.Permission.objects.filter(url__contains=url)
    elif isNone(name) == False and isNone(url) == True:
        permissions = models.Permission.objects.filter(name__contains=name)
    elif isNone(name) == True and isNone(url) == True:
        permissions = models.Permission.objects.all()
    elif isNone(name) == False and isNone(url) == False:
        permissions = models.Permission.objects.filter(name__contains=name,url__contains=url)

    dataCount = permissions.count()
    list = []
    for permission in permissions:
        dict = {}
        dict['id'] = permission.id
        dict['name'] = permission.name
        dict['url'] = permission.url
        dict['describe'] = permission.describe
        list.append(dict)

    pageIndex = request.GET.get('page')
    pageSize = request.GET.get('limit')
    paginator = Paginator(list, pageSize)
    datas = paginator.page(pageIndex)
    res = []
    for data in datas:
        res.append(data)
    contact = {"code": 0, "msg": "成功", "count": dataCount, "data": res}
    return JsonResponse(contact)

def del_permission(request):
    id=request.GET.get('id')
    count=models.Permission.objects.filter(id=id).delete()

    user = models.User.objects.filter(id=request.session['userid'])[0]
    permissions = models.Role_Permission.objects.filter(Role_id=user.Role.id)
    permissionids = []
    for permission in permissions:
        permissionids.append(permission.Permission.id)
    permissions = models.Permission.objects.filter(id__in=permissionids)
    urls = []
    for permission in permissions:
        urls.append(permission.url)
    request.session['permissions'] = urls


    if count==1:
        return JsonResponse({'msg':'success'})
    return JsonResponse({'msg':'fail'})

def addpermission(request):
    return render(request, 'rmsystem/addpermission.html')

def add_permission(request):
    name = request.GET.get('name')
    url = request.GET.get('url')
    describe = request.GET.get('describe')
    permission=models.Permission.objects.create(name=name,url=url,describe=describe)
    permission.save()
    return JsonResponse({'msg':'success'})

def editpermission(request):
    name=request.GET.get('name')
    url=request.GET.get('url')
    describe=request.GET.get('describe')
    data={'name':name,'url':url,'describe':describe}
    return render(request, 'rmsystem/editpermission.html', data)

def add_permission(request):
    name = request.GET.get('name')
    url = request.GET.get('url')
    describe = request.GET.get('describe')
    permission=models.Permission.objects.create(name=name,url=url,describe=describe)
    permission.save()
    return JsonResponse({'msg':'success'})

def edit_permission(request):
    id = request.GET.get('id')
    name = request.GET.get('name')
    url = request.GET.get('url')
    describe = request.GET.get('describe')
    models.Permission.objects.filter(id=id).update(name=name,url=url,describe=describe)

    user = models.User.objects.filter(id=request.session['userid'])[0]
    permissions = models.Role_Permission.objects.filter(Role_id=user.Role.id)
    permissionids = []
    for permission in permissions:
        permissionids.append(permission.Permission.id)
    permissions = models.Permission.objects.filter(id__in=permissionids)
    urls = []
    for permission in permissions:
        urls.append(permission.url)
    request.session['permissions'] = urls

    return JsonResponse({'msg':'success'})

def allroles(request):
    return render(request, 'rmsystem/allroles.html')

def get_allroles(request):
    name = request.GET.get('name')
    if isNone(name) == True:
        roles = models.Role.objects.all()
    elif isNone(name) == False:
        roles = models.Role.objects.filter(name__contains=name)

    dataCount = roles.count()
    list = []
    for role in roles:
        dict = {}
        dict['id'] = role.id
        dict['name'] = role.name
        dict['describe'] = role.describe
        list.append(dict)

    pageIndex = request.GET.get('page')
    pageSize = request.GET.get('limit')
    paginator = Paginator(list, pageSize)
    datas = paginator.page(pageIndex)
    res = []
    for data in datas:
        res.append(data)
    contact = {"code": 0, "msg": "成功", "count": dataCount, "data": res}
    return JsonResponse(contact)

def del_role(request):
    id=request.GET.get('id')
    count=models.Role.objects.filter(id=id).delete()
    if count==1:
        return JsonResponse({'msg':'success'})
    return JsonResponse({'msg':'fail'})

def addrole(request):
    return render(request, 'rmsystem/addrole.html')

def add_role(request):
    name = request.GET.get('name')
    describe = request.GET.get('describe')
    role=models.Role.objects.create(name=name,describe=describe)
    role.save()
    return JsonResponse({'msg':'success'})

def editrole(request):
    name=request.GET.get('name')
    describe=request.GET.get('describe')
    roleid = request.GET.get('roleid')
    data={'name':name,'describe':describe,'roleid':roleid}

    return render(request, 'rmsystem/editrole.html', data)

def add_role(request):
    name = request.GET.get('name')
    describe = request.GET.get('describe')
    selects=json.loads(request.GET.get('select'))
    print(selects)
    role = models.Role.objects.create(name=name, describe=describe)
    for select in selects:
        models.Role_Permission.objects.create(Role_id=role.id,Permission_id=select)

    return JsonResponse({'msg':'success'})

def edit_role(request):
    roleid = request.GET.get('roleid')
    name = request.GET.get('name')
    describe = request.GET.get('describe')
    new_permissions=json.loads(request.GET.get('selects'))
    models.Role.objects.filter(id=roleid).update(name=name,describe=describe)
    old_permissions=[]
    role_permissions=models.Role_Permission.objects.filter(Role_id=roleid)
    for role_permission in role_permissions:
        old_permissions.append(role_permission.Permission.id)


    for permissionid in set(old_permissions)-set(new_permissions):
        models.Role_Permission.objects.filter(Role_id=roleid,Permission_id=permissionid).delete()

    for permissionid in set(new_permissions) - set(old_permissions):
        models.Role_Permission.objects.create(Role_id=roleid,Permission_id=permissionid)

    user = models.User.objects.filter(id=request.session['userid'])[0]
    permissions = models.Role_Permission.objects.filter(Role_id=user.Role.id)
    permissionids = []
    for permission in permissions:
        permissionids.append(permission.Permission.id)
    permissions = models.Permission.objects.filter(id__in=permissionids)
    urls = []
    for permission in permissions:
        urls.append(permission.url)
    request.session['permissions'] = urls

    return JsonResponse({'msg':'success'})

def get_allpermission(request):
    permissions = models.Permission.objects.all()
    list = []
    for permission in permissions:
        dict = {}
        dict['id'] = permission.id
        dict['name'] = permission.name
        dict['url'] = permission.url
        dict['describe'] = permission.describe
        list.append(dict)
    return JsonResponse({'data':list})

def get_x(request):


    roleid=request.GET.get('roleid')
    permissions = models.Permission.objects.all()
    list = {}
    for permission in permissions:
        dict = {}
        dict['id'] = permission.id
        dict['name'] = permission.name
        dict['selected']=''
        list[permission.id]=(dict)

    role_permissions = models.Role_Permission.objects.filter(Role_id=roleid)
    for role_permission in role_permissions:
        list[role_permission.Permission.id]['selected']='selected'

    res=[]
    for value in list.values():
        res.append(value)
    print(res)
    return JsonResponse({'data':res})

def userinfo(request):
    userid=request.GET.get('userid')
    return render(request, 'rmsystem/userinfo.html', {'userid':userid})

def get_userinfo(request):
    userid = request.GET.get('userid')
    user = models.User.objects.filter(id=userid)
    userinfo = {}
    userinfo['userid'] = user[0].id
    userinfo['username'] = user[0].username
    userinfo['sex'] = user[0].sex
    userinfo['phone'] = user[0].phone
    userinfo['email'] = user[0].email
    userinfo['remarks'] = user[0].remarks
    userinfo['head'] = user[0].head
    return JsonResponse(userinfo)

def edit_userinfo(request):
    userid= request.GET.get('userid')
    username = request.GET.get('username')
    sex = request.GET.get('sex')
    phone = request.GET.get('phone')
    email = request.GET.get('email')
    remarks = request.GET.get('remarks')
    userid = request.GET.get('userid')
    roleid = request.GET.get('roleid')
    models.User.objects.filter(id=userid).update(username=username,sex=sex,phone=phone,email=email,remarks=remarks,Role_id=int(roleid))

    user = models.User.objects.filter(id=userid)[0]
    permissions = models.Role_Permission.objects.filter(Role_id=user.Role.id)
    permissionids = []
    for permission in permissions:
        permissionids.append(permission.Permission.id)
    permissions = models.Permission.objects.filter(id__in=permissionids)
    urls = []
    for permission in permissions:
        urls.append(permission.url)
    request.session['permissions'] = urls


    return JsonResponse({'msg':'success'})

def get_userhasrole(request):
    userid=request.GET.get('userid')
    users=models.User.objects.filter(id=userid)
    roles=models.Role.objects.all()
    list=[]
    for role in roles:
        dict={}
        dict['id']=role.id
        dict['name']=role.name
        list.append(dict)
    return JsonResponse({'data':list,'hasroleid':users[0].Role.id})

def allrecords(request):
    return render(request, 'rmsystem/allrecords.html')

def get_allrecords(request):
    userid=request.GET.get('userid')
    selectdate=request.GET.get('date')
    selecttitle=request.GET.get('title')
    print(selectdate,selecttitle)


    if isNone(selectdate) == True and isNone(selecttitle) == False:
        movies = models.Movie.objects.filter(title__contains=selecttitle)
        movieids=[]
        for movie in movies:
            movieids.append(movie.id)
        records=models.Record.objects.filter(User_id=userid,Movie_id__in=movieids)
    elif isNone(selectdate) == False and isNone(selecttitle) == True:
        date_from_to=selectdate.split(' - ')
        date_from=datetime.datetime.strptime(date_from_to[0],'%Y-%m-%d')
        date_to = datetime.datetime.strptime(date_from_to[1], '%Y-%m-%d')
        date_to=date_to.replace(hour=23)
        date_to=date_to.replace(minute=59)
        date_to=date_to.replace(second=59)
        records = models.Record.objects.filter(User_id=userid,time__range=(date_from,date_to))
    elif isNone(selectdate) == True and isNone(selecttitle) == True:
        records = models.Record.objects.filter(User_id=userid)
    elif isNone(selectdate) == False and isNone(selecttitle) == False:
        movies = models.Movie.objects.filter(title__contains=selecttitle)
        movieids = []
        for movie in movies:
            movieids.append(movie.id)
        date_from_to = selectdate.split(' - ')
        date_from = datetime.datetime.strptime(date_from_to[0], '%Y-%m-%d')
        date_to = datetime.datetime.strptime(date_from_to[1], '%Y-%m-%d')
        date_to = date_to.replace(hour=23)
        date_to = date_to.replace(minute=59)
        date_to = date_to.replace(second=59)
        records = models.Record.objects.filter(User_id=userid, Movie_id__in=movieids,time__range=(date_from,date_to))

    dataCount=records.count()
    list=[]
    for record in records:
        dict={}
        dict['movieid']=record.Movie.id
        dict['title']=models.Movie.objects.filter(id=record.id)[0].title
        dict['time']=record.time
        dict['click']=record.click
        list.append(dict)

    pageIndex = request.GET.get('page')
    pageSize = request.GET.get('limit')
    paginator = Paginator(list, pageSize)
    datas = paginator.page(pageIndex)
    res = []
    for data in datas:
        res.append(data)
    contact = {"code": 0, "msg": "成功", "count": dataCount, "data": res}
    return JsonResponse(contact)

def clear_records(request):
    userid=request.GET.get('userid')
    models.Record.objects.filter(User_id=userid).delete()
    return JsonResponse({'msg':'success'})