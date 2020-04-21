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

def get_average():
    data=[]
    #x=[110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]
    x=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
    for i in x:
        f = open('result/500_1000_'+str(i)+'_280_dynucb3.txt','r')
        y = json.loads(f.read())
        data.append(np.average(y))
        print(i,np.average(y))
    plt.plot(x,data)
    plt.show()

def get_data():
    i=180
    f = open('result/500_1000_0.2_' + str(i) + '_dynucb.txt', 'r')
    y = json.loads(f.read())
    for i in range(len(y)):
        print(i,y[i])

if __name__=='__main__':
    f = open('result/dynucb/500_1000_0.2_220_dynucb3.txt', 'r')
    y = json.loads(f.read())
    f = open('result/500_1000_0.15_linucb.txt', 'r')
    y1 = json.loads(f.read())
    plt.plot(range(len(y)),y)
    plt.plot(range(len(y1)), y1)
    plt.show()