import csv
import pandas as pd
import numpy as np
import numpy.matlib
import sys
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
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix

class CofibaUser:
    def __init__(self,userID,featureDimension):
        self.d=featureDimension
        self.I=np.identity(featureDimension)
        self.A=self.I
        self.AInv=np.linalg.inv(self.A)
        self.b=np.zeros([featureDimension,1])
        self.theta=np.dot(self.AInv,self.b)
        self.id=userID

    def updateParameter(self,moviePicked_FeatureVector,click):
        self.A+=np.outer(moviePicked_FeatureVector,moviePicked_FeatureVector)
        self.b+=click*moviePicked_FeatureVector
        self.AInv=np.linalg.inv(self.A)
        self.theta=np.dot(self.AInv,self.b)

    def getScore(self,alpha,users,neighUserNum,pool_Movies,time):
        CA = self.A
        CB = self.b
        dict_user_q={}
        for user in users:
            dist=np.linalg.norm(user.theta.T[0]-self.theta.T[0])
            dict_user_q[user.id]=dist


        neighUser = sorted(dict_user_q.items(), key=lambda x: x[1])[0:neighUserNum]
        #print(neighUser)

        y=neighUserNum
        for item in neighUser:
            if np.linalg.norm(users[item[0]].theta.T[0])==0 or np.linalg.norm(self.theta.T[0])==0:
                q=0
            else:
                q = np.inner(users[item[0]].theta.T[0], self.theta.T[0]) / (np.linalg.norm(users[item[0]].theta.T[0]) * np.linalg.norm(self.theta.T[0]))
                if q>0.9:
                    CA+=q*(users[item[0]].A-self.I)
                    CB+=q*(users[item[0]].b)


        CAInv=np.linalg.inv(CA)
        mean = np.dot(CAInv,CB)
        maxPTA = float('-inf')

        for x in pool_Movies:
            temp=np.dot(np.dot(x.featureVector.T, CAInv), x.featureVector)[0][0]*math.log(time+2,math.e)
            if temp<0:
                var=0
            else:
                var = math.sqrt(temp)
            score=np.dot(mean.T,x.featureVector)[0][0]+alpha*var
            if maxPTA < score:
                picked = x
                maxPTA = score
        return picked

class Movie:
    def __init__(self,movieID,featureVector,title):
        self.id=movieID
        self.featureVector=featureVector
        self.title=title


class Cofiba:
    def __init__(self, dimension, alpha, n,neighUserNum):
        self.time = 0
        self.dimension = dimension
        self.alpha = alpha
        self.record=pd.DataFrame(pd.read_csv('ml-latest/cofiba/tag1.csv'))
        self.userNum=n
        # init record
        self.record['hasRecommend']=[False]*len(self.record)
        self.UserNeighbor={}
        self.neighUserNum=neighUserNum
        # Every user host an algorithm which operates a linear bandit algorithm
        self.users = []
        for i in range(n):
            self.users.append(CofibaUser(i,dimension))

        # init movies
        pd_movies=pd.DataFrame(pd.read_csv('ml-latest/cofiba/movie.csv'))

        self.movies=[]
        i=0
        for index,row in pd_movies.iterrows():
            self.movies.append(Movie(i,np.array(json.loads(row['feature'])),row['title']))
            i+=1
        self.movieNum = len(self.movies)


    def decide(self, pool_movies, userID,time):
        picked = self.users[userID].getScore(self.alpha,self.users,self.neighUserNum,pool_movies,time)
        return picked

    def get_movieCandidates(self, userID, num_candidate):
        candidate = []  # 候选集
        user_watched_movieId = self.record.loc[self.record['userId'] == userID].loc[:,
                               ['movieId', 'timestamp', 'hasRecommend']]

        index = user_watched_movieId.loc[user_watched_movieId['hasRecommend'] == False]['timestamp'].argmin()
        candidate.append(self.movies[user_watched_movieId.iat[index, 0]])

        list_nuwatch_movieId = sample(
            set(range(self.movieNum)) ^ set(user_watched_movieId.loc[:, 'movieId'].values.tolist()),
            num_candidate - 1)
        for movie in list_nuwatch_movieId:
            candidate.append(self.movies[movie])
        return candidate

    def test(self,times):
        data_ctr=[]
        for t in range(times):
            clicks = 0
            n = 0
            start_time=time.time()
            for user in self.users:

                candidates = self.get_movieCandidates(user.id, 20)
                picked = self.decide(candidates, user.id,t)

                if picked.id==candidates[0].id:
                    user.updateParameter(self.movies[picked.id].featureVector,1)
                    self.record.loc[self.record['userId'] == user.id].loc[self.record['movieId'] == picked.id].loc[:,'hasRecommend'] = True
                    clicks+=1
                else:
                    user.updateParameter(self.movies[picked.id].featureVector, 0)
                n+=1

            ctr=clicks/n
            print('第' + str(t) + '轮的点击率:' + str(ctr)+'   耗时：'+str(time.time()-start_time))
            data_ctr.append(ctr)
        file = open('result/' + str(self.userNum) + '_' + str(times) + '_' + str(self.alpha)+'_'+str(self.neighUserNum)+ '_COLINBA.txt', 'w')
        file.write(json.dumps(data_ctr))
        file.close()

if __name__=='__main__':
    cofiba=Cofiba(10,0.8,500,20)
    cofiba.test(500)
