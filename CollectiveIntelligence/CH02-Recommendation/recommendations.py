#-*-coding=utf-8-*-

#-----------------------
# Named:    Recommendation
# Created:  2016-07-25
# @Author:  Qianfeng
#-----------------------

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
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
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


# 相似度度量
from math import sqrt

def sim_distance(prefs, persion1, persion2):
    # 仅测量是否对物品有行为
    si = {}
    for item in prefs[persion1]:
        if item in prefs[persion2]:
            si[item] = 1

    if len(si) == 0:
        return 0

    sum_of_squares = sum([pow(prefs[persion1][item] - prefs[persion2][item],2)
         for item in prefs[persion1] if item in prefs[persion2]])

    return 1/(1+sqrt(sum_of_squares))


# 返回 p1 和 p2 的相关系数
def sim_pearson(prefs, p1, p2):
    # 获取双方都曾评价过的物品列表
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # 获取列表元素个数
    n = float(len(si))

    # 两者无共同处，返回1
    if n == 0:
        return 0

    # 对所有偏好求和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # 求平方和
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])

    # 求乘积之和
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # 计算皮尔逊评价值
    num = pSum - (sum1 * sum2/n)
    den = sqrt((sum1Sq - pow(sum1,2)/n) * (sum2Sq - pow(sum2,2)/n))
    if den == 0:
        return 0

    r = num/den
    return r

def sim_tanimoto(prefs, p1, p2):
    p1Set = set(prefs[p1])
    p2Set = set(prefs[p2])
    intersectSet = p1Set.intersection(p2Set)
    unionSet = p1Set.union(p2Set)
    return len(intersectSet)/float(len(unionSet)-len(intersectSet)+1)



# ---------------------------
# 从反映偏好的字典中返回最为匹配者
#返回结果的个数和相似度函数均为可选参数
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]

    # 对列表进行排序，评价最高者排在最前
    scores.sort(key=lambda x: x[0], reverse=True)
    # scores.reverse() 可与上述排序方法替换
    return scores[:n]

#----------------------------
# 利用所有他人评价值的加权平均，为客户提供推荐
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        if other == person:
            continue
        sim = similarity(prefs, person, other)

        # 忽略评价值为零活小于零的情况
        if sim<=0:
            continue
        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                totals.setdefault(item,0)
                totals[item] += prefs[other][item] * sim
                simSums[item] = simSums.get(item, 0) + sim

        # 创建归一化列表
        rankings = [(total/simSums[item],item) for item,total in totals.items()]

        # 返回经过排序的列表
        rankings.sort(key=lambda x:x[0], reverse=True)
        return rankings


# =========================
# 基于物品的推荐
# 人与物品对调
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    # 建立字典，以给出与这些物品最为相近的所有其他物品
    result = {}

    # 以物品为中心对偏好矩阵实施倒置处理
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # 针对大数据集更新状态变量
        c += 1
        if c%100 == 0:
            print '%d / %d' % (c,len(itemPrefs))
        # 寻找最相近的物品
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # 循环遍历由当前用户评分的物品
    for (item, rating) in userRatings.items():

        # 循环遍历与当前物品相近的物品
        for (similarity, item2) in itemMatch[item]:
            # 如果该用户已经对当前物品做过评价
            if item2 in userRatings:
                continue

            # 评价值与相似度的加权之和
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # 全部相似度之和
            # totalSim.setdefault(item2, 0)
            # totalSim[item2] += similarity
            totalSim[item2] = totalSim.get(item2,0) + similarity
    
    # 将每个合计值处理加权和，求出平均值
    rankings = [(score/totalSim[item], item) for item,score in scores.items()]

    # 按最高值到最低值的顺序，返回评分结果
    rankings.sort(key=lambda x: x[0], reverse=True)
    return rankings

# 使用 MovieLens 数据集
def loadMovieLens(path='D:\\tmp'):
    # 获取影片标题
    movies = {}
    for line in open(path+'\\u.item'):
        (id,title) = line.split('|')[0:2]
        movies[id] = title

    # 加载数据
    prefs = {}
    for line in open(path+'\\u.data'):
        (user, movieid, rating, ts) = line.split('\t')
        prefs.setdefault(user,{})
        prefs[user][movies[movieid]] = float(rating)
    return prefs


# 基于用户过滤的改进
def calculateSimilarUsers(prefs, n=5):
    # 预先计算用户相似度
    result = {}

    c = 0
    for user in prefs:
        # 针对大数据集更新状态变量
        c += 1
        if c%100 == 0:
            print '%d / %d' % (c,len(itemPrefs))
        # 寻找最相近的物品
        scores = topMatches(prefs, user, n=n, similarity=sim_pearson)
        result[user] = scores
    return result


def getUserRecommendations(prefs, userMatch, user):
    scores = {}
    simTotal = {}

    for (score,user) in userMatch[user].items():
        for (item,rating) in prefs[user]:
            scores.setdefault(item, 0)
            scores[item] += score * rating

            simTotal[item] += simTotal.get(item,0) + score
    rankings = [(score/simTotal[item], item) for score,item in scores.items()]
    rankings.sort(key=lambda x: x[0], reverse=True)
    return rankings

