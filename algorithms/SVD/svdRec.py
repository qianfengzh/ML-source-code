#-*-coding=utf-8-*-

#-----------------------
# Named:    SVD (Singular Conmponent Decomposition)
# Created:  2016-07-21
# @Author:  Qianfeng
#-----------------------

import numpy as np
from numpy import linalg as la

def loadData():
    return [[1,1,1,0,0],
            [2,2,2,0,0],
            [1,1,1,0,0],
            [5,5,5,0,0],
            [1,1,0,2,2],
            [0,0,0,3,3],
            [0,0,0,1,1]]
def loadDataTmp():
    return [[4,4,0,2,2],
            [4,0,0,3,3],
            [4,0,0,1,1],
            [1,1,1,2,0],
            [2,2,2,0,0],
            [1,1,1,0,0],
            [5,5,5,0,0]]

def loadExData2():
    return[[0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 5],
           [0, 0, 0, 3, 0, 4, 0, 0, 0, 0, 3],
           [0, 0, 0, 0, 4, 0, 0, 1, 0, 4, 0],
           [3, 3, 4, 0, 0, 0, 0, 2, 2, 0, 0],
           [5, 4, 5, 0, 0, 0, 0, 5, 5, 0, 0],
           [0, 0, 0, 0, 5, 0, 1, 0, 0, 5, 0],
           [4, 3, 4, 0, 0, 0, 0, 5, 5, 0, 1],
           [0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 4],
           [0, 0, 0, 2, 0, 2, 5, 0, 0, 1, 2],
           [0, 0, 0, 0, 5, 0, 0, 0, 0, 4, 0],
           [1, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0]]


def ecluSim(inA, inB):
    return 1.0/(1.0 + la.norm(inA - inB))

def pearsSim(inA, inB):
    if len(inA) < 3:
        return 1.0
    return 0.5 + 0.5*np.corrcoef(inA, inB, rowvar=0)[0][1]

def cosSim(inA, inB):
    num = float(inA.T * inB)
    denom = la.norm(inA) * la.norm(inB)
    return 0.5 + 0.5*(num/denom)


# 基于物品相似度的推荐引擎
def standEst(dataMat, user, simMeas, item): # item 为用户未评价过的物品
    n = np.shape(dataMat)[1]
    simToal = 0.0
    ratSimTotal = 0.0
    # print 'the item is:',item
    for j in range(n): # 遍历所有物品
        userRating = dataMat[user, j]
        if userRating == 0: # 用户对物品没有评价
            continue
        # 寻找两个用户都评级的物品（获得用户索引） overLap: array-1D
        overLap = np.nonzero(np.logical_and(dataMat[:,item].A>0, dataMat[:,j].A>0))[0]
        # print 'the overLap is:',overLap

        if len(overLap) == 0:
            similarity = 0
        else:
            similarity = simMeas(dataMat[overLap,item], dataMat[overLap,j])
            # print 'the dataMat[overLap,item] is:',dataMat[overLap,item]
        # print 'the %d and %d similarity is: %f' % (item, j, similarity)
        simToal += similarity
        ratSimTotal += similarity * userRating # 利用用户的评价来对相似度加权
    if simToal == 0:
        return 0
    else:
        return ratSimTotal/simToal

def recommend(dataMat, user, N=3, simMeas=cosSim, estMethod=standEst):
    unratedItems = np.nonzero(dataMat[user,:].A==0)[1] # 寻找未评级的物品
    if len(unratedItems) == 0:
        return 'you reated everthing'
    itemScores = []
    for item in unratedItems:
        estimatedScore = estMethod(dataMat, user, simMeas, item)
        itemScores.append((item, estimatedScore))
    # 寻找前 N 个未评过等级的物品
    return sorted(itemScores, key=lambda jj: jj[1], reverse=True)[:N]


# 基于 SVD 的评分估计
def svdEst(dataMat, user, simMeas, item):
    n = np.shape(dataMat)[1]
    simTotal = 0.0
    ratSimTotal = 0.0
    U, Sigma, VT = la.svd(dataMat)
    Sig4 = np.mat(np.eye(4) * Sigma[:4])
    xformedItems = dataMat.T * U[:,:4] * Sig4.I
    for j in range(n):
        userRating = dataMat[user,j]
        if userRating == 0 or j == item:
            continue
        similarity = simMeas(xformedItems[item,:].T, xformedItems[j,:].T)
        print 'the %d and %d similarity is: %f' % (item, j, similarity)
        simTotal += similarity
        ratSimTotal += similarity * userRating
    if simTotal == 0:
        return 0
    else:
        return ratSimTotal/simTotal



# SVD 图像压缩

def printMat(inMat, thresh=0.8):
    for i in range(32):
        for k in range(32):
            if float(inMat[i,k]) > thresh:
                print 1
            else:
                print 0
        print ''

def imgCompress(numSV=3, thresh=0.8):
    myl = []
    for line in open('D:\\tmp\\0_5.txt').readlines():
        newRow = []
        for i in range(32):
            newRow.append(int(line[i]))
        myl.append(newRow)
    myMat = np.mat(myl)
    print '****original matrix****'
    print np.shape(myMat)
    print myMat
    U, Sigma, VT = la.svd(myMat)
    SigRecon = np.mat(np.zeros((numSV, numSV)))
    for k in range(numSV):
        SigRecon[k,k] = Sigma[k]
    reconMat = U[:,:numSV] * SigRecon*VT[:numSV,:]
    print '****SVD****'
    print np.shape(reconMat)
    # printMat(reconMat, thresh)











