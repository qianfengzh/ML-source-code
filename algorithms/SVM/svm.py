#-*-coding=utf-8-*-

#-----------------------
# Named:    kNN
# Created:  2016-07-13
# @Author:  Qianfeng
#-----------------------

import random
import numpy as np

def loadDataSet(fileName):
    dataMat = []
    labelMat = []
    fr = open(fileName)
    for line in fr.readlines():
        lineArr = line.strip().split('\t')
        dataMat.append([float(lineArr[0]), float(lineArr[1])])
        labelMat.append(float(lineArr[2]))
    return dataMat, labelMat

def selectJrand(i, m): # 随机选取一个不同于 i 的 j，用于两个 alpha的同时优化
    j=i
    while (j==i):
        j = int(random.uniform(0,m))
    return j

def clipAlpha(aj, H, L):
    if aj > H:
        aj = H
    if aj < L:
        aj = L
    return aj

#-------------------------------------------------

def smoSimple(dataMatIn, classLabels, C, toler, maxIter):
    dataMatrix = np.mat(dataMatIn)
    labelMat = np.mat(classLabels.transpose())
    b = 0
    m, n = dataMatrix.shape
    alphas = np.mat(np.zeros((m,1)))
    iter = 0
    while (iter < maxIter):
        alphaPairsChanged = 0
        for i in range(m):
            fXi = float(np.multiply(alphas, labelMat).T *\
                (dataMatrix * dataMatrix[i,:].T)) + b
            Ei = fXi - float(labelMat[i])
            if ((label[i]*Ei < -toler) and (alphas[i]<C)) or\
                ((label[i]*Ei > toler) and (alphas[i]>0)): # 如果alpha可以改进优化过程
                j = selectJrand(i, m)
                fXj = float(np.multiply(alphas, labelMat).T *\
                    (dataMatrix*dataMatrix[j,:].T)) + b
                Ej = fXj - float(labelMat[j])
                alphaIold = alphas[i].copy()
                alphaJold = alphas[j].copy()

                if(labelMat[i] != labelMat[j]):
                    L = max(0, alphas[j] - alphas[i])
                    H = min(C, C + alphas[j] - alphas[i])
                else:
                    L = max(0, alphas[j] + alphas[i] - C)
                    H = min(C,alphas[j] + alphas[i])
                if L==H:
                    print 'L==H'
                    continue
                eta = 2.0 * dataMatrix[i,:] * dataMatrix[j,:].T-\
                    dataMatrix[i,:] * dataMatrix[i,:].T-\
                    dataMatrix[j,:] * dataMatrix[j,:].T

                # 对 i 进行修改，修改量与 j 相同，但方向相反
                if eta >= 0:
                    print 'eta>=0'
                    continue
                alphas[j] -= labelMat[j] *(Ei-Ej)/eta
                alphas[j] = clipAlpha(alphas[j],H,L)
                if (np.abs(alphas[j] - alphaJold) < 0.00001):
                    print 'j not moving enough'
                    continue
                alphas[i] += labelMat[j] * labelMat[i] *\
                    (alphaJold - alphas[j])
                b1 = b - Ei -labelMat[i] *(alphas[i]-alphaIold)*\
                    dataMatrix[i,:] * dataMatrix[i,:].T - labelMat[j]*\
                    (alphas[j]-alphaJold)*dataMatrix[i,:]*dataMatrix[j,:].T
                b2 = b - Ej -labelMat[i] * (alphas[i]-alphaIold)*\
                    dataMatrix[i,:]*dataMatrix[j,:].T - \
                    labelMat[j] * (alphas[j] - alphaJold)*\
                    dataMatrix[j,:] * (dataMatrix[j,:].T)
                if (0 < alphas[i]) and (C > alphas[i]):
                    b = b2
                else:
                    b = (b1+b2)/2.0
                alphaPairsChanged += 1
                print 'iter: %d i: %d, pairs changed %d' % (iter, i, alphaPairsChanged)
        if (alphaPairsChanged == 0):
            iter += 1
        else:
            iter = 0
        print 'iteration number: %d' % iter
    return b, alphas















