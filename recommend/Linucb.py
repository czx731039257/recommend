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

    def getScore(self,movie_FeatureVector,alpha):
        mean = np.dot(self.AInv,self.b)
        var = math.sqrt(np.dot(np.dot(movie_FeatureVector.T,self.AInv),movie_FeatureVector))
        score=np.dot(mean.T,movie_FeatureVector)[0][0]+alpha*var
        return score

class Movie:
    def __init__(self,movieID,featureVector,title):
        self.id=movieID
        self.featureVector=featureVector
        self.title=title


class Cofiba:
    def __init__(self, dimension, alpha, n):
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


    def decide(self, pool_movies, userID):
        maxPTA = -100

        for x in pool_movies:
            x_pta = self.users[userID].getScore(x.featureVector,self.alpha)
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
            clicks = 0
            n = 0
            for user in self.users:
                candidates = self.get_movieCandidates(user.id, 20)
                picked = self.decide(candidates, user.id)
                MovieClusterNum = picked.id  # Get the cluster number of item
                if picked.id==candidates[0].id:
                    user.updateParameter(self.movies[picked.id].featureVector,1)
                    self.record.loc[self.record['userId'] == user.id].loc[self.record['movieId'] == picked.id].loc[:,'hasRecommend'] = True
                    clicks+=1
                else:
                    user.updateParameter(self.movies[picked.id].featureVector, 0)
                n+=1

            ctr=clicks/n
            print('第' + str(t) + '轮的点击率:' + str(ctr))
            data_ctr.append(ctr)
        file = open('result/' + str(self.userNum) + '_' + str(times) + '_' + str(self.alpha) + '_linucb.txt', 'w')
        file.write(json.dumps(data_ctr))
        file.close()

if __name__=='__main__':
    cofiba=Cofiba(10,0.2,500)
    cofiba.test(1000)
    cofiba = Cofiba(10, 0.15, 500)
    cofiba.test(1000)
    cofiba = Cofiba(10, 0.25, 500)
    cofiba.test(1000)
