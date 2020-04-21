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

    def getScore(self,cluster,movie_FeatureVector,alpha,userID,users):
        CA=self.I
        Cb=np.zeros([self.d,1])
        for i in range(len(cluster)):
            if cluster[i]==cluster[userID]:
                CA+=(users[i].A-self.I)
                Cb+=users[i].b
        CAInv=np.linalg.inv(CA)
        mean = np.dot(CAInv,Cb)
        var = math.sqrt(np.dot(np.dot(movie_FeatureVector.T,CAInv),movie_FeatureVector))
        score=np.dot(mean.T,movie_FeatureVector)[0][0]+alpha*var
        return score

class Movie:
    def __init__(self,movieID,featureVector,title):
        self.id=movieID
        self.featureVector=featureVector
        self.title=title


class Cofiba:
    def __init__(self, dimension, alpha, alpha_2, n, cluster_init='Erdos-Renyi'):
        self.time = 0
        self.dimension = dimension
        self.alpha = alpha
        self.alpha_2 = alpha_2
        self.cluster_init = cluster_init
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

        # Init a single cluster over item set
        '''if self.cluster_init == 'Erdos-Renyi':
            p = 3 * math.log(self.movieNum) / self.movieNum
            self.MGraph = np.random.choice([0, 1], size=(self.movieNum, self.movieNum), p=[1 - p, p])
        else:
            self.MGraph = np.ones([self.movieNum, self.movieNum])
        self.Mclusters = []
        N_components_Movie, components_Movie = connected_components(csr_matrix(self.MGraph))
        self.Mclusters = components_Movie
        self.N_components_Movie = N_components_Movie'''

        # Init a family of clusters over users set
        self.UGraph = []
        self.Uclusters = []
        for i in range(self.movieNum):
            print(i)
            if self.cluster_init == 'Erdos-Renyi':
                p = 3 * math.log(n) / n
                self.UGraph.append(np.random.choice([0, 1], size=(n, n), p=[1 - p, p]))
            else:
                self.UGraph.append(np.ones([n, n]))
            self.Uclusters.append([])
            N_components_U, components_U = connected_components(csr_matrix(self.UGraph[i]))
            self.Uclusters[i] = components_U

        self.UserNeighbor = {}


    def decide(self, pool_movies, userID):
        maxPTA = -100

        for x in pool_movies:
            x_pta = self.users[userID].getScore(self.Uclusters[x.id],x.featureVector,self.alpha, userID,self.users)
            if maxPTA < x_pta:
                picked = x
                maxPTA = x_pta
        self.time += 1

        return picked


    def updateUserClusters(self, userID, articlePicked_FeatureVector, MovieClusterNum):
        n = len(self.users)
        for j in range(n):
            diff = math.fabs(
                np.dot(self.users[userID].theta.T, articlePicked_FeatureVector) - np.dot(self.users[j].theta.T,
                                                                                           articlePicked_FeatureVector))
            CB = self.alpha_2 * (np.sqrt(np.dot(np.dot(articlePicked_FeatureVector.T, self.users[userID].AInv),
                                                articlePicked_FeatureVector)) + np.sqrt(
                np.dot(np.dot(articlePicked_FeatureVector.T, self.users[j].AInv),
                       articlePicked_FeatureVector))) * np.sqrt(np.log10(self.time + 1))
            # print float(np.linalg.norm(self.users[userID].UserTheta - self.users[j].UserTheta,2)),'R', ratio
            if diff > CB:
                self.UGraph[MovieClusterNum][userID][j] = 0
                self.UGraph[MovieClusterNum][j][userID] = self.UGraph[MovieClusterNum][userID][j]
        N_components, component_list = connected_components(csr_matrix(self.UGraph[MovieClusterNum]))
        # print 'N_components:',N_components
        self.Uclusters[MovieClusterNum] = component_list
        return N_components

    def updateMovieClusters(self, userID, chosenMovie, MovieClusterNum):
        m = self.movieNum
        n = len(self.users)

        for a in self.movies:
            if self.MGraph[chosenMovie.id][a.id] == 1:
                self.UserNeighbor[a.id] = np.ones([n,n])
                for i in range(n):
                    diff = math.fabs(
                        np.dot(self.users[userID].theta.T, a.featureVector) - np.dot(self.users[i].theta.T,
                                                                                       a.featureVector))
                    CB = self.alpha_2 * (np.sqrt(
                        np.dot(np.dot(a.featureVector.T, self.users[userID].AInv), a.featureVector)) + np.sqrt(
                        np.dot(np.dot(a.featureVector.T, self.users[i].AInv), a.featureVector))) * np.sqrt(
                        np.log10(self.time + 1))
                    if diff > CB:
                        self.UserNeighbor[a.id][userID][i] = 0
                        self.UserNeighbor[a.id][i][userID] = 0
                if not np.array_equal(self.UserNeighbor[a.id], self.UGraph[MovieClusterNum]):
                    self.MGraph[chosenMovie.id][a.id] = 0
                    self.MGraph[a.id][chosenMovie.id] = 0
                # print 'delete edge'
        self.N_components_Item, component_list_Item = connected_components(csr_matrix(self.MGraph))
        self.Mclusters = component_list_Item

        # For each new item cluster, allocate a new connected graph over users representing a single user clsuter
        self.UGraph = []
        self.Uclusters = []
        for i in range(self.N_components_Item):
            if self.cluster_init == 'Erdos-Renyi':
                p = 3 * math.log(len(self.users)) / len(self.users)
                self.UGraph.append(np.random.choice([0, 1], size=(len(self.users), len(self.users)), p=[1 - p, p]))
            else:
                self.UGraph.append(np.ones([len(self.users), len(self.users)]))
            self.Uclusters.append([])
            N_components_U, components_U = connected_components(csr_matrix(self.UGraph[i]))
            self.Uclusters[i] = components_U
        return self.N_components_Item

    def get_movieCandidates(self,userID,num_candidate):
        candidate = []  # 候选集
        user_watched_movieId = self.record.loc[self.record['userId'] == userID].loc[:, ['movieId', 'timestamp']]

        index = user_watched_movieId.loc[self.record['hasRecommend'] == False]['timestamp'].argmin()
        candidate.append(self.movies[user_watched_movieId.iat[index, 0]])

        list_nuwatch_movieId = sample(set(range(self.movieNum)) ^ set(user_watched_movieId.loc[:, 'movieId'].values.tolist()),
                                      num_candidate - 1)
        for movie in list_nuwatch_movieId:
            candidate.append(self.movies[movie])
        return candidate

    def test(self,times):
        clicks=0
        n=0
        data_ctr=[]
        for t in range(times):
            start_time=time.time()
            for user in self.users:
                candidates = self.get_movieCandidates(user.id, 20)
                picked = self.decide(candidates, user.id)
                MovieClusterNum = picked.id  # Get the cluster number of item
                self.updateUserClusters(user.id, picked.featureVector,MovieClusterNum)  # get the user clustering based on item x
                #self.updateMovieClusters(user.id,picked,MovieClusterNum)
                if picked.id==candidates[0].id:
                    user.updateParameter(self.movies[picked.id].featureVector,1)
                    self.record.loc[ self.record['userId']==user.id].loc[ self.record['movieId']==picked.id].loc[:,'hasRecommend']=True
                    clicks+=1
                else:
                    user.updateParameter(self.movies[picked.id].featureVector, 0)
                n+=1

            ctr=clicks/n
            print('第' + str(t) + '轮的点击率:' + str(ctr)+'     耗时：'+str(time.time()-start_time))
            data_ctr.append(ctr)
        file = open('result/' + str(self.userNum) + '_' + str(times) + '_' + str(self.alpha) + '_y.txt', 'w')
        file.write(json.dumps(data_ctr))
        file.close()

if __name__=='__main__':
    cofiba=Cofiba(10,0.4,0.3,500,'asd')
    cofiba.test(500)
