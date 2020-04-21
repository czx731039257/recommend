import urllib.request as urllib2  #将urllib2库引用进来
import re
import requests
import pandas as pd
from lxml import etree
import time
import random
from bs4 import BeautifulSoup as bs
import json
from urllib.request import urlretrieve
from translate import baidu_fanyi
import urllib
opener = urllib2.build_opener()#构建一个handler对象


headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
}

Agent=[
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'User-Agent:Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'User-Agent:Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'User-Agent:Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'User-Agent:Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'
]



def get_movie_msg(movieid,name):

    timeout=5

    #随机伪造用户
    headers={
        'User-Agent':random.choice(Agent)
    }

    #随机获取代理ip
    ip=get_proxyip()
    proxies={
        "http":ip
    }



    #随机获取停顿时间
    toptime=random.randint(5,15)
    time.sleep(timeout)


    name=name.strip().replace(',','%2C')
    name=name.replace(' ','%20')
    year=name[-5:-1]
    name=name.replace('(','%28')
    name = name.replace(')','%29')
    url = 'https://www.douban.com/search?cat=1002&q='+name
    #print(url)
    html = requests.get(url,headers=headers,proxies=proxies).text
    #print(html)
    html=etree.HTML(html)
    src=html.xpath('//div[@class="search-result"]/div[@class="result-list"]/div[@class="result"]/div[@class="content"]//span[@class="subject-cast" and contains(text(),"'+year+'")]/../preceding-sibling::h3/span[contains(text(),"电影")]/../a/@href')
    #print('src:',src)

    if len(src)==0:
        return False,'nosrc'

    html = requests.get(src[0],headers=headers,proxies=proxies).text

    html=etree.HTML(html)
    title=html.xpath('//div[@id="wrapper"]/div[@id="content"]/h1/span[@property="v:itemreviewed"]/text()')
    print('电影名:',title)
    img=html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="mainpic"]//img/@src')[0]
    print('图片:',img)
    #urllib.request.urlretrieve(img, 'D:\\pythonproject\\recommend\\ml-latest\\cofiba\\picture\\'+str(movieid)+'.jpg')
    time.sleep(random.randint(2,5))
    picture = requests.get(img,headers=headers)
    with open('D:\\pythonproject\\recommend\\ml-latest\\cofiba\\picture\\'+str(movieid)+'.jpg', 'wb') as f:
        f.write(picture.content)
        f.close()
    director=html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="info"]//span[contains(text(),"导演") and @class="pl"]/following-sibling::span[1]/a/text()')
    print('导演:',director)
    scriptwriter = html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="info"]//span[contains(text(),"编剧") and @class="pl"]/following-sibling::span[1]/a/text()')
    print('编剧:', scriptwriter)
    actor = html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="info"]/span/span[contains(text(),"主演") and @class="pl"]/following-sibling::span[1]/a/text()')
    print('主演:', actor)
    type = html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="info"]/span[@property="v:genre"]/text()')
    print('类型:', type)
    releasetime=html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="info"]//span[contains(text(),"上映日期") and @class="pl"]/following-sibling::span[1]/text()')
    print('上映时间',releasetime)
    runtime = html.xpath('//div[@id="wrapper"]/div[@id="content"]//div[@id="info"]/span[@property="v:runtime"]/@content')
    print('时长:', runtime)
    summary= html.xpath('//div[@id="wrapper"]//span[@class="all hidden"]/text()')
    if len(summary)==0:
        summary = html.xpath('//div[@id="wrapper"]//span[@property="v:summary"]/text()')
        if len(summary)==0:
            summary=['']
    for i in range(len(summary)):
        summary[i]=summary[i].replace('\u3000',' ')
        summary[i]=summary[i].replace('\n',' ')
        summary[i]=summary[i].strip()


    print('剧情简介:', summary)
    return title,img,director,scriptwriter,actor,type,releasetime,runtime,summary

def getall(start,end):
    movies = pd.DataFrame(pd.read_csv('ml-latest/cofiba/movie.csv'))

    for index, row in movies.iterrows():
        if index<start or index>end:
            continue
        print(index)
        result=get_movie_msg(row['movieId'],row['title'])
        if len(result)==2:
            if result[1]=='timeout':
                while len(result)==2 and result[1]=='timeout':
                    result=get_movie_msg(row['title'])
                if len(result)==2:
                    continue
            elif result[1]=='nosrc':
                print('没有找到资源')
                continue

        save(row['movieId'],result)


def save(movieId,msg):
    title=msg[0]
    img=msg[1]
    director=msg[2]
    scriptwriter=msg[3]
    actor=msg[4]
    type=msg[5]
    releasetime=msg[6]
    runtime=msg[7]
    summary=msg[8]
    text={}
    text['title']=title
    text['img']=img
    text['director']=json.dumps(director)
    text['scriptwriter']=json.dumps(scriptwriter)
    text['actor']=json.dumps(actor)
    text['type']=json.dumps(type)
    text['releasetime'] = json.dumps(releasetime)
    text['runtime']=json.dumps(runtime)
    text['summary']=json.dumps(summary)

    print(text)
    file=open('ml-latest/cofiba/detail/'+str(movieId)+'.text','w')
    file.write(json.dumps(text))
    file.close()

def get(movieId):
    file=open('ml-latest/cofiba/detail/'+str(movieId)+'.text','r')
    text=json.loads(file.read())
    title = text['title']
    img = text['img']
    director = json.loads(text['director'])
    scriptwriter = json.loads(text['scriptwriter'])
    actor = json.loads(text['actor'])
    type = json.loads(text['type'])
    releasetime=json.loads(text['releasetime'])
    runtime = json.loads(text['runtime'])
    summary = json.loads(text['summary'])
    print('电影名:',title)
    print('图片:',img)
    print('导演:',director)
    print('编剧:',scriptwriter)
    print('主演:',actor)
    print('类型:',type)
    print('上映时间',releasetime)
    print('时长:',runtime)
    print('剧情简介:',summary)

def get_proxyip():
    url_getip='http://d.jghttp.golangapi.com/getip?num=20&type=1&pro=0&city=0&yys=0&port=1&pack=20152&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=2&regions='
    url_addip='http://webapi.jghttp.golangapi.com/index/index/save_white?neek=18053&appkey=f4bfce2fa4a6fd7c15f08eed14444686&white=183.25.168.11'
    response = requests.get(url_getip)
    text = response.text
    while text.__contains__('{'):
        print(text)
        time.sleep(1)
        response = requests.get(url_getip)
        text = response.text

    text=text.split(':')
    ip={
        "host" : text[0],
        "port" : text[1][0:4],
    }
    print('代理ip:',ip)
    return ip

if __name__=='__main__':
    getall(2833,5282)
    #msg=get_movie_msg(0,'Toy Story (1995)')
    #save(0,msg)
    #get(0)

