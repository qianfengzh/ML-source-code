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
    n = len(si)

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
def getRecommendation(prefs, person, similarity=sim_pearson):
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




