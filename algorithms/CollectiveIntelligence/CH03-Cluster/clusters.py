#-*-coding=utf-8-*-

#-----------------------
# Named:    Blog Cluster
# Created:  2016-07-27
# @Author:  Qianfeng
#-----------------------

def readfile(filename):
    lines[line for line in file(filename)]

    # 第一行是列标题
    colnames = lines[0].strip().split('\t')[1:]
    rowname = []
    data = []
    for line in lines[1:]:
        p = line.strip().split('\t')
        # 每行的第一列是列名
        rownames.append(p[0])
        # 剩余部分是该行的数据
        data.append([float[x] for x in p[1:]])
    return rownames, colnames, data

from math import sqrt
def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    sum1Sq = sum([pow(v,2) for v in v1])
    sum2Sq = sum([pow(v,2) for v in v2])

    pSum = sum([v1[i] * v2[i] for i in range(len(v1))])

    num = pSum - (sum1 * sum2/len(v1))
    den = sqrt((sum1Sq - pow(sum1,2)/len(v1)) * (sum2Sq - pow(sum2,2)/len(v1)))

    '''
    # numpy实现
    import numpy as np
    return np.corrcoef(v1,v2)[0][1]
    '''

    if den == 0:
        return 0
    return 1.0-num/den  #将相似度转化为距离（相似度越大，距离越小）


#claster类
class bicluster:
    def __init__  _(self, vec, left=None, right=None, distance=0.0, id=None):
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance

def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1

    #最开始的聚类就是数据集中的行
    clust = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0,1)
        closest = distance(clust[0].vect, clust[1].vect)

        #遍历每一个配对，寻找最小距离 <笛卡尔积>
        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                #用distance 来缓存距离的计算值
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)] = distance(clust[i].vect, clust[j].vect)

                d = distances[(clust[i].id, clust[j].id)]

                if d<closest:
                    closest = d
                    lowestpair = (i, j)
        #计算两个聚类的平均值
        mergevec = [(clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i])/2.0\
        for i in range(len(clust[0].vec))]

        #建立新的聚类
        newcluster = bicluster(mergevec, left=clust[lowestpair[0]],\
            right=clust[lowestpair[1]],distance=closest,id=currentclustid)

        #不在原始集合中的聚类，其id为负数
        currentclustid -= 1
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    return clust[0]  #返回最终的一个 bicluster 对象

