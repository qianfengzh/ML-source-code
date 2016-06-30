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





