import csv
import pandas as pd
import numpy as np
import numpy.matlib
import json
import random
from gensim import corpora
from matplotlib import pyplot as plt
import gensim
import math
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
import time
from random import sample






class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


# 处理电影用户标签文件，得到的磁带放入文件wordbag.txt文件
def get_wordbag():
    print('开始提取词袋')
    time_start=time.time() #计时

    movies = pd.DataFrame(pd.read_csv('ml-latest/movies.csv'))
    movieAndTag = pd.DataFrame(pd.read_csv('ml-latest/tags.csv'))

    size_movies = len(movies)
    movies=movies.loc[:,['movieId','title']]
    movies['index']=np.arange(size_movies)
    wordbag = np.zeros([size_movies, 0]).tolist()

    en_stop = get_stop_words('en')  # 获取english的停顿词表
    tokenizer = RegexpTokenizer(r'\w+')
    p_stemmer = PorterStemmer() # 提取词干
    for line, row in movieAndTag.iterrows():
        tags = tokenizer.tokenize(str(row['tag']).strip().lower())
        index = movies.loc[movies['movieId'] == int(row['movieId'])].iat[0, 2]
        for tag in tags:
            if not tag in en_stop:
                wordbag[index].append(p_stemmer.stem(tag))

    file = open('wordbag.txt', 'w', encoding='UTF-8')
    file.write(json.dumps(wordbag))
    file.close()
    time_end = time.time()
    print('词袋提取完成，并且存入到wordbag.txt文件。耗时:'+str(time_end-time_start))


# 过滤电影，筛选掉评语少于least_word的电影，返筛选后的新词袋和新电影集合
def filter_data(least_word):
    movies = pd.DataFrame(pd.read_csv('ml-latest/movies.csv')) # 电影信息文件

    # 读取wordbag.txt文件的数据，并使用json对读取的磁带进行编码转化成list类型
    wordbag=json.loads(open('wordbag.txt', 'r').read())
    sum=[]
    for words in wordbag:
        sum.append(len(words))
    movies['word']=wordbag
    movies['sum']=sum
    new_movies=movies.loc[movies['sum']>=least_word]
    new_wordbag=new_movies.loc[:,'word'].values.tolist()
    return new_wordbag,new_movies


def lda(num_topics,passes):
    print('开始训练lda模型')
    time_start = time.time()  # 计时

    wordbag,movies = filter_data(50)
    # 创建语料的词语词典，每个单独的词语都会被赋予一个索引
    dictionary = corpora.Dictionary(wordbag)

    # 使用上面的词典，将转换文档列表（语料）变成 DT 矩阵(文本-单词矩阵)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in wordbag]
    Lda = gensim.models.ldamodel.LdaModel

    print('开始训练主题模型')
    # 在 DT 矩阵上运行和训练 LDA 模型
    ldamodel = Lda(doc_term_matrix, num_topics=num_topics, id2word = dictionary, passes=passes)
    print('主题模型训练完成')

    docs = ldamodel[doc_term_matrix]
    for doc in docs:
        print(doc)

    json_docs = []
    for doc in docs:
        x=np.zeros([num_topics,1],dtype=np.float)
        for value in doc:
            x[value[0]][0]=value[1]
        json_docs.append(json.dumps(x.tolist(), cls=NumpyEncoder))
    movies['feature'] = json_docs

    movies.to_csv('ml-latest/filtered_movies.csv',index=False,sep=',') #写入new_movies文件
    moviesAndTag = pd.DataFrame(pd.read_csv('ml-latest/tags.csv'))
    filtered_moviesAndTag = moviesAndTag.loc[moviesAndTag['movieId'].isin(movies.loc[:,'movieId'].values)]
    filtered_moviesAndTag.to_csv('ml-latest/filtered1_tags.csv', index=False, sep=',') #写入new_tags文件
    time_end = time.time()
    print('训练lda主题模型完成，并且通过每部电影的标签数过滤掉movies.csv和tags.csv文件，最后分别保存到filtered_movies.csv和filtered1_tags。csv文件中。耗时:' + str(time_end - time_start))

def user_tagssum():
    movieAndTag = pd.DataFrame(pd.read_csv('ml-latest/filtered1_tags.csv'))
    userId_list = list(set(movieAndTag.loc[:, 'userId'].values))
    d = {}
    for userId in userId_list:
        d[userId] = np.size(movieAndTag.loc[movieAndTag['userId'] == userId].values)
    userId_list = np.array(sorted(d.items(), key=lambda x: x[1], reverse=True))[..., 0].tolist()
    file=open('user_tagsum.txt','w')
    file.write(json.dumps(userId_list))
    file.close()

# 获取活跃度前number的用户id列表
def get_users(number):
    file=open('user_tagsum.txt','r')
    users=json.loads(file.read())[0:number]
    file.close()
    return users

# 获取电影id的列表
def get_movies():
    movies=pd.DataFrame(pd.read_csv('ml-latest/filtered_movies.csv'))
    return movies

# 获取过滤后的用户观看记录
def get_filtered1_tags():
    tags=pd.DataFrame(pd.read_csv('ml-latest/filtered1_tags.csv'))
    return tags

def get_filtered2_tags(userId_list):
    tags = pd.DataFrame(pd.read_csv('ml-latest/filtered1_tags.csv'))
    tags=tags.loc[tags['userId'].isin(userId_list)]
    tags['index']=range(len(tags))
    groupby = tags.groupby(['userId', 'movieId'])
    #filtered2_tags = pd.DataFrame(columns=['userId', 'movieId', 'tag', 'timestamp'])

    indexs=[]
    for name, group in groupby:
        #filtered2_tags = filtered2_tags.append(group.iloc[group['timestamp'].argmin(), :], ignore_index=True)
        if len(group)>1:
            indexs.append(tags.at[group['timestamp'].idxmin(),'index'])

        else:
            indexs.append(tags.iat[0,4])
    #filtered2_tags=filtered2_tags.astype({'userId':'int64','movieId':'int64','timestamp':'int64'})
    #return filtered2_tags
    tags=tags.loc[tags['index'].isin(indexs)]
    return tags

# 获取电影候选集
def get_movieCandidates(userid,tags,movies,num_candidate):
    candidate=[] #候选集
    user_watched_movieId = tags.loc[tags['userId'] == userid].loc[:,['movieId','timestamp']]

    index=user_watched_movieId.loc[tags['hasRecommend'] == False]['timestamp'].argmin()
    candidate.append(user_watched_movieId.iat[index,0])
    '''size_movies=len(movies)
    i=0
    # 随机生成该用户没有看多的电影
    while i<num_candidate-1:
        index=random.randint(0,size_movies-1)
        if not user_watched_movieId.__contains__(movies[index]):
            candidate.append(movies[index])
            i+=1'''
    list_nuwatch_movieId=sample(set(movies)^set(user_watched_movieId.loc[:,'movieId'].values.tolist()),num_candidate-1)
    for movie in list_nuwatch_movieId:
        candidate.append(movie)
    return candidate

# 获取得分
def get_socres(A,b,movieFeatures,rate_learn):
    thet=np.dot(np.linalg.inv(A),b)
    score=np.dot(thet.T,movieFeatures)+rate_learn*math.sqrt(np.dot(np.dot(movieFeatures.T,np.linalg.inv(A)),movieFeatures))
    return score




def linucb(num_topic,num_user,round,rate_learn):
    num_candidate = 20
    movies=get_movies()
    movieId_list = list(set(movies.loc[:, 'movieId']))
    #movieId_list.sort()
    usersId_list=get_users(num_user)
    pd_tags=get_filtered2_tags(usersId_list)
    #pd_tags=get_filtered1_tags()
    pd_tags['hasRecommend']=[False]*len(pd_tags)
    A=[]
    b=[]

    for i in range(len(usersId_list)):
        A.append(np.matlib.identity(num_topic).tolist())
        b.append(np.matlib.zeros((num_topic,1)).tolist())
    user_parameters=pd.DataFrame([],index=usersId_list)
    user_parameters['A']=A
    user_parameters['b'] = b

    data_ctr=[]
    data_t=[]
    for t in range(round):
        n=0 #展示数
        r=0 #点击数
        i=0
        for userId in usersId_list:
            # print(i)
            i+=1
            if len(pd_tags.loc[pd_tags['userId']==userId].loc[pd_tags['hasRecommend']==False])==0:
                continue
            else:
                list_movieCandidates=get_movieCandidates(userId,pd_tags,movieId_list,num_candidate) # 获取该用户的候选集
                maxscore=0
                movieId_maxscore=0
                for movieId in list_movieCandidates:
                    x=json.loads(movies.loc[movies['movieId']==movieId].iat[0,5])
                    score=get_socres(np.array(user_parameters.at[userId,'A']),np.array(user_parameters.at[userId,'b']),np.array(x),rate_learn)
                    if score>maxscore:
                        maxscore=score
                        movieId_maxscore=movieId
                A=np.array(user_parameters.at[userId,'A'])
                b=np.array(user_parameters.at[userId,'b'])
                #print(movieId_maxscore)
                #print(movies.loc[movies['movieId']==movieId_maxscore])
                x=np.array(json.loads(movies.loc[movies['movieId']==movieId_maxscore].iat[0,5]))
                user_parameters.loc[userId,'A']=np.add(A,np.dot(x.T,x))
                if movieId_maxscore==list_movieCandidates[0]:
                    user_parameters.loc[userId,'b']=np.add(b,x)
                    pd_tags.loc[pd_tags['userId']==userId].loc[pd_tags['movieId']==movieId_maxscore].loc[:,'hasRecommend']=True
                    r+=1
                n+=1
        ctr=r/n
        print('第' + str(t) + '轮的点击率:' + str(ctr))
        data_ctr.append(ctr)
        data_t.append(t)
    file=open('result/'+str(num_user)+'_'+str(round)+'_'+str(rate_learn)+'_y.txt','w')
    file.write(json.dumps(data_ctr))
    file.close()

    '''plt.title(str(num_user)+'_'+str(round)+'_'+str(rate_learn))
    plt.xlabel('Round')
    plt.ylabel('ctr')
    plt.plot(data_t,data_ctr)
    plt.show()'''

def drawing(num_user,round,rate_learn):
    y=json.loads(open('result/'+str(num_user)+'_'+str(round)+'_'+str(rate_learn)+'_y.txt','r').read())
    return y

def get_average():
    i = 0.1
    a = []
    while i <= 0.7:
        x, y = drawing(100, 2000, i)
        a.append(np.average(y))
        i += 0.1
    print(a)

if __name__== '__main__':
    y = drawing(500, 500, 0.4)
    y1=drawing(500,500,0.7)
    x=range(500)
    plt.ylim(0,1)
    plt.plot(x,y)
    plt.plot(x,y1)
    plt.show()