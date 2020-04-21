from math import pow, sqrt
import operator
""""静态的推荐算法"""
class Usercf:
    def __init__(self, data):
        self.data = data
    def pearson(self, user1, user2):
        n = 0
        sumXY = 0
        sumX = 0
        sumY =0
        sumX2 = 0
        sumY2 = 0
        for movie, score in self.data[user1].items():
            if movie in self.data[user2].keys():
                n +=1
                sumXY +=score*self.data[user2][movie]
                sumX +=score
                sumY +=self.data[user2][movie]
                sumX2 +=pow(score, 2)
                sumY2 +=pow(self.data[user2][movie], 2)
        molecule = sumXY - (sumX*sumY)/n
        denominator = sqrt((sumX2-pow(sumX, 2)/n)*(sumY2-pow(sumY, 2)/n))
        r = molecule/denominator
        return r

    def nearstUser(self, username, n=1):
        distances = {}
        for otheruser in self.data.keys():
            if otheruser != username:
                distance = self.pearson(username, otheruser)
                distances[otheruser] = distance
        sortedDistance = sorted(distances.items(), key=operator.itemgetter(1), reverse=True)
        print(sortedDistance)
        return sortedDistance[:n]

    def recomand(self, username, n=1):
        sortedDistance = self.nearstUser(username, n)
        recomandMovie = {}
        for name, distance in dict(sortedDistance).items():
            print('\n推荐人： ', (name, distance))
            for movie, socre in self.data[name].items():
                if movie not in self.data[username].keys():
                    print(name+'为该用户推荐: ', (movie, socre))
                if movie not in self.data[username].keys() and movie not in recomandMovie.keys():
                    recomandMovie[movie] = socre
        sortedMovie = sorted(recomandMovie.items(), key=operator.itemgetter(1), reverse=True)
        print('最终推荐：%s'%sortedMovie)

if __name__ == '__main__':
    users = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                           'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                           'The Night Listener': 3.0},

             'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                              'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                              'You, Me and Dupree': 3.5},

             'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                  'Superman Returns': 3.5, 'The Night Listener': 4.0},

             'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                              'The Night Listener': 4.5, 'Superman Returns': 4.0,
                              'You, Me and Dupree': 2.5},

             'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                              'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                              'You, Me and Dupree': 2.0},

             'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                               'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},

             'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}
             }
    usercf = Usercf(users)
    usercf.recomand('Toby', 2)
