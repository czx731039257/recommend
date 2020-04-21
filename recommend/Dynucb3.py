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
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix

class CofibaUser:
    def __init__(self,userID,featureDimension,clusterID):
        self.d=featureDimension
        self.I=np.identity(featureDimension)
        self.A=self.I
        self.AInv=np.linalg.inv(self.A)
        self.b=np.zeros([featureDimension,1])
        self.theta=np.dot(self.AInv,self.b)
        self.id=userID
        self.clusterID=clusterID

    def updateParameter(self,moviePicked_FeatureVector,click):
        self.A+=np.outer(moviePicked_FeatureVector,moviePicked_FeatureVector)
        self.b+=click*moviePicked_FeatureVector
        self.AInv=np.linalg.inv(self.A)
        self.theta=np.dot(self.AInv,self.b)

    def getScore(self,movie_FeatureVector,alpha,cluster,time):
        mean = cluster[self.clusterID].theta
        var = math.sqrt(np.dot(np.dot(movie_FeatureVector.T,cluster[self.clusterID].AInv),movie_FeatureVector)*math.log(time+2,math.e))
        score=np.dot(mean.T,movie_FeatureVector)[0][0]+alpha*var
        return score

class Movie:
    def __init__(self,movieID,featureVector,title):
        self.id=movieID
        self.featureVector=featureVector
        self.title=title


class Cluster:
    def __init__(self,dimension,id,users):
        self.id=id
        self.dimension=dimension
        self.users=users
        self.I=np.identity(dimension)
        self.A=self.I
        self.b=np.zeros([dimension,1])
        self.compute_parameter()

    def delete_user(self,userID):
        if len(self.users)==1:
            self.compute_parameter()
            return False
        del_index=-1
        for i in range(len(self.users)):
            if self.users[i].id==userID:
                del_index=i
        del self.users[del_index]
        self.compute_parameter()
        return True

    def compute_parameter(self):
        self.A = self.I
        self.b = np.zeros([self.dimension, 1])
        for user in self.users:
            self.A+=(user.A-self.I)
            self.b+=user.b
        self.AInv=np.linalg.inv(self.A)
        self.theta=np.dot(self.AInv,self.b)

    def add_user(self,user):
        self.users.append(user)
        self.compute_parameter()


class Cofiba:
    def __init__(self, dimension, alpha, n,clusterNum):
        self.time = 0
        self.dimension = dimension
        self.alpha = alpha
        self.record=pd.DataFrame(pd.read_csv('ml-latest/cofiba/tag1.csv'))
        self.userNum=n
        # init record
        self.record['hasRecommend']=[False]*len(self.record)
        self.UserNeighbor={}
        # Every user host an algorithm which operates a linear bandit algorithm
        self.users = []
        self.clusterNum=clusterNum
        self.clusters=[]
        usercluster = []
        for i in range(clusterNum):
            usercluster.append([])

        for i in range(n):
            user=CofibaUser(i,dimension,i%clusterNum)
            self.users.append(user)
            usercluster[i%clusterNum].append(user)

        for i in range(clusterNum):
            self.clusters.append(Cluster(dimension,i,usercluster[i]))




        # init movies
        pd_movies=pd.DataFrame(pd.read_csv('ml-latest/cofiba/movie.csv'))

        self.movies=[]
        i=0
        for index,row in pd_movies.iterrows():
            self.movies.append(Movie(i,np.array(json.loads(row['feature'])),row['title']))
            i+=1
        self.movieNum = len(self.movies)


    def decide(self, pool_movies, userID,time):
        maxPTA = -100

        for x in pool_movies:
            x_pta = self.users[userID].getScore(x.featureVector,self.alpha,self.clusters,time)
            if maxPTA < x_pta:
                picked = x
                maxPTA = x_pta
        self.time += 1

        return picked

    def get_movieCandidates(self, userID, num_candidate):
        candidate = []  # 候选集
        user_watched_movieId = self.record.loc[self.record['userId'] == userID].loc[:,['movieId', 'timestamp', 'hasRecommend']]
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
            #for cluster in self.clusters:
                #print(cluster.id, len(cluster.users))
            clicks = 0
            n = 0
            for user in self.users:
                candidates = self.get_movieCandidates(user.id, 20)
                picked = self.decide(candidates, user.id,t)
                MovieClusterNum = picked.id  # Get the cluster number of item
                if picked.id==candidates[0].id:
                    user.updateParameter(self.movies[picked.id].featureVector,1)
                    self.record.loc[self.record['userId'] == user.id].loc[self.record['movieId'] == picked.id].loc[:,'hasRecommend'] = True
                    clicks+=1
                else:
                    user.updateParameter(self.movies[picked.id].featureVector, 0)
                min_value=100000000
                min_index=0
                for cluster in self.clusters:
                    value=np.linalg.norm(cluster.theta-user.theta)
                    if value<min_value:
                        min_value=value
                        min_index=cluster.id
                if not min_index==user.clusterID:
                    flag=self.clusters[user.clusterID].delete_user(user.id)
                    if flag==True:
                        user.clusterID=min_index
                        self.clusters[min_index].add_user(user)
                else:
                    self.clusters[user.clusterID].compute_parameter()
                n+=1
            ctr=clicks/n
            print('第' + str(t) + '轮的点击率:' + str(ctr))
            data_ctr.append(ctr)
        file = open('result/' + str(self.userNum) + '_' + str(times) + '_' + str(self.alpha)+'_'+str(self.clusterNum)+ '_dynucb3.txt', 'w')
        file.write(json.dumps(data_ctr))
        file.close()

if __name__=='__main__':
    cofiba = Cofiba(10, 0.1, 500, 280)
    cofiba.test(1000)
    cofiba = Cofiba(10, 0.3, 500, 280)
    cofiba.test(1000)
    cofiba = Cofiba(10, 0.4, 500, 280)
    cofiba.test(1000)
    cofiba = Cofiba(10, 0.5, 500, 280)
    cofiba.test(1000)


