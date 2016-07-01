#-*- coding=utf-8 -*-



import math
#------------------------
# 一、推荐系统评测指标
# (用户满意度、预测准确度、覆盖率、多样性、新颖性、惊喜度
#  、信任度、实时性、健壮性、商业目标)
#------------------------

# 2、预测准确度

# 1）评分
def RMSE(records):
    """
    均方根误差测算预测准确度
    param:
      rui->用户u对物品i的实际评分
      pui->预测用户u对物品i的结果
    有平方项，相比MAE对评测更加苛刻，对错误惩罚更大
    """
    return math.sqrt(sum([(rui-pui)*(rui-pui) for u,i,rui,pui in records]) / float(len(records)))

def MAE(records):
    """
    绝对值误差测算预测准确度
    param:
      rui->用户u对物品i的实际评分
      pui->预测用户u对物品i的结果
    """
    reture sum([abs(rui-pui) for u,i,rui,pui in records]) / fload(len(records))


# 2）topN
# topN 一般通过 precision 和 recall 来度量
def PrecisionRecall(test, N):
    """
    test 位用户行为与结果字典，N为推荐列表长度
    一般会选不同的推荐列表长度，求出一组 recall 和 precision 画 precision/recall curve
    """
    hit = 0
    n_recall = 0
    n_precision = 0
    for user,items in test.items():
        rank = Recommend(user, N)
        hit += len(rank & items)
        n_recall += len(items)
        n_precision += N
    return [hit / (1.0 * n_recall), hit / (1.0 * n_precision)]


# 3、覆盖率(coverage)
"""
覆盖率的两个著名度量指标：信息熵、Gini指数
"""
def GiniIndex(p):
    """
    给定物品流行度分布p(item,weight)，计算基尼指数
    """
    j = 1
    n = len(p)
    G = 0
    for item, weight in sorted(p.items(), key=itemgetter(1)):
        G += (2 * j - n - 1) * weight
    return G / float(n-1)

# 4、多样性，使用同一推荐列表中物品的向异性来度量
#   排列组合注意去重！

# 5、新颖性，即用户未进行行为过的物品
#     可通过推荐结果的平均流行度来度量，平均流行度越低，则证明越新颖

# 6、惊喜度
#   如果推荐结果和用户的历史兴趣不相似，但却让用户觉
#   得满意，那么就可以说推荐结果的惊喜度很高，而推荐的新颖性仅仅取决于用户是否听说过这个
#   推荐结果。

# 7、信任度
#    增加推荐系统透明度，结合社交网络系统

# 8、实时性
#   1>推荐列表变化速率；2>新物品的推荐能力（即物品的冷启动问题）

# 9、健壮性（推荐系统的反作弊问题）

# 10、商业目的




#------------------------
# 二、基于用户行为数据推荐
# 协同过滤算法（基于邻域的方法、隐语义模型、基于图的随机游走算法）
#  MovieLens数据集： http://www.grouplens.org/node/73
#------------------------
import random
def SplitData(data, M, k, seed):
    """
    将数据data 切分为 M 个部分，k为每次试验选取不同测试集和训练集
    """
    test = []
    train = []
    random.seed(seed)
    for user, item in data:
        if random.randint(0,M) == k:
            test.append([user,item])
        else:
            train.append([user,item])
    return train, test


def Recall(train, test, N):
    """
    Evaluation: by recall rate
    """
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += len(tu)
    return hit / (all * 1.0)


def Precision(train, test, N):
    """
    Evaluation: by precision rate
    """
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += N
    return hit / (all * 1.0)


def Coverage(train, test, N):
    """
    Evaluation: by coverage
    """
    recommend_items = set()
    all_items = set()
    for user in train.keys():
        for item in train[user].keys():
            all_items.add(item)
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            recommend_items.add(item)
    return len(recommend_items) / float(all_items)


def Popularity(train, test, N):
    """
    Evaluation: by popularity
    利用所有推荐出物品的平均流行度来评测 算法的新颖性

    在计算平均流行度时对每个物品的流行度取对数，这是因为物品的流行度分布满足长
    尾分布，在取对数后，流行度的平均值更加稳定
    """
    item_popularity = dict()
    for user, items in train.items():
        for item in items.keys():
            if item not in item_popularity:
                item_popularity[item] = 0
            item_popularity[item] += 1
    ret = 0
    n = 0
    for user in train.keys():
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            ret += math.log(1 + item_popularity[item])
            n += 1
    ret /= float(n)
    return ret


#---------------
# USER-CF
#---------------
def UserSimilarity0(train):
    """
    利用余弦相似度 实现 用户见相似度度量
    """
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue
            W[u][v] = len(train[u] & train[v])
            W[u][v] /= math.sqrt(len(train[u]) * len(train[v]) * 1.0)
    return W


def UserSimilarity1(train):
    # 建立物品到用户的倒排表
    item_users = dict()
    for u, items in train.items():
        for i in item.keys():
            if i not in item_users: # 倒排表初始化
                item_users[i] = set()
            item_users[i].add(u) # 理论上（此处只查看用户是否对物品有操作，并非要去汇总用户对物品的操作数）


    C = dict()
    N = dict()
    for i, users in item_users.items():
        for u in users:
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                C[u][v] += 1

    # 计算最终的相似矩阵
    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
    return W



def Recommend(user, train, W):
    """
    u v 的相似度矩阵，与 用户v 的兴趣物品之积，求和
    """
    rank = dict()
    interacted_items = train[user]
    for v, wuv in sorted(W[u].items, key=itemgetter(1), reverse=True)[0:K]:
        for i, rvi in train[v].items:
            if i in interacted_items: # 将用户行为过的物品进行滤除，只推荐用户没有见过的
                continue
            rank[i] += wuv * rvi
    return rank


def UserSimilarity2(train):
    """
    基于原有Jaccaard 系数计算相似度的改进
    对不同用户共同兴趣列表中的热门商品做了惩罚，以减少对相似度的影响
    """
    # build inverse table for item_users
    item_users = dict()
    for u, items in train.items():
        for i in items.keys():
            if i not in item_uses:
                item_users[i] = set()
            item_users[i].add(u)

    # calculate co_rated items between users
    C = dict()
    N = dict()
    for i,users in item_users.items():
        for u in users:
            N[u] += 1
            for v in users:
                if v == u:
                    continue
                C[u][v] += 1/math.log(1 + len(users)) # 使用 除法，将热门商品的影响与冷门商品的影响拉平

    # caculate finial similarity matrix W
    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(len(N[u]) * len(N[v]))
    return W # 用户相似度矩阵




#--------------
# ITEM-CF
#--------------

def ItemSimilarity0(train):
    """
    同USER-CF一样，形成物品倒排表，计算物品相似度
    """
    # caculate co-rated users between items
    C = dict()
    N = dict()
    for u, itmes in train.items():
        for i in items:
            N[i] += 1
            for j in items:
                if i == j:
                    continue
                C[i][j] += 1
    # clculate finial similarity matrix W
    W = dict()
    for i, related_items in C.items():
        for j, cij in related_items:
            W[i][j] = cij / math.sqrt(N[i] * N[j])
    return W # 返回商品相似度矩阵


def RecommendationItem-CF(train, user_id, W, K):
    """
    基于物品的协同过滤推荐
    """
    rank = dict()
    ru = train(user_id)
    for i, pi in ru.items(): # 对需要推荐用户的有操作历史的所有物品，找出 K 个最相似的物品
        for j, wj in sorted(W[i].items(), key=itemgetter(1), reverse=True)[0:K]:
            if j in ru:
                continue
            rank[j] += pi * wj # wj 为物品i、j 之间的相似度值，pi为用户对物品 i 的历史兴趣度
    return rank

def RecommendationItem-CF(train, user_id, W, K):
    """
    基于物品的推荐（携带解释）
    """
    rank = dict()
    ru = train[user_id]
    for i, pi in ru.items():
        for j, wj in sorted(W[i].items(), key=itemgetter(1), reverse=True)[0:K]:
            if j in ru:
                continue
            rank[j].weight += pi * wj
            rank[j].reason[i] = pi * wj
    return rank

def ItemSimilarity1(train):
    """
    ItemCF-IUF
    
    基于原有相似度计算的改进，软性惩罚过于活跃用户的影响
    """
    # calculate co-rated uses between items
    C = dict()
    N = dict()
    for u, items in train.items():
        for i in items:
            N[i] += 1
            for j in items:
                if i == j:
                    continue
                C[i][j] += 1 / math.log(1 + len(items) * 1.0)

    # calculate finial similarity matrix W
    W = dict()
    for i, related_items in C.items():
        for j, cij in related_items.items():
            W[i][j] = cij / math.sqrt(N[i] * N[j])
    return W




