#-*-coding=utf-8-*-

#-----------------------
# Named:	K-Means
# Created:	2016-07-17
# @Author:	Qianfeng
#-----------------------

import numpy as np
import random

def loadDataSet(fileName):
	datMat = []
	fr = open(fileName)
	for line in fr.readlines():
		curLine = line.strip().split('\t')
		fltLine = map(float, curLine)
		datMat.append(fltLine)
	return datMat

def disEclud(vecA, vecB):
	return np.sqrt(sum(np.power(vecA - vecB), 2))


def randCent(dataSet, k):
	n = np.shape(dataSet)[1]
	centroids = np.mat(np.zeros((k,n)))
	for j in range(n): # 随机初始化质心
		minJ = min(dataSet[:,j])
		rangeJ = float(max(dataSet[:,j]) - minJ)
		centroids[:,j] = minJ + rangeJ * random.rand(k,1) # 每次初始化所有质心的一个特征列
	return centroids

#------------------------------------------

def kMeans(dataSet, k, distMeas=disEclud, createCent=randCent):
	m = np.shape(dataSet)[0]
	clusterAssment = np.mat(np.zeros((m,2)))
	centroids = createCent(dataSet, k)
	clusterChanged = True
	while clusterChanged: # 循环迭代更新质心，直到所有点的隶属不在变化
		clusterChanged = False
		for i in range(m): # 对所有点计算与各质心距离，划分隶属
			minDist = np.inf
			minIndex = -1
			for j in range(k):
				distJI = distMeas(centroids[j,:], dataSet[i,:])
				if distJI = < minDist:
					minDist = distJI
					minIndex = j
			if clusterAssment[i,0] != minIndex: # 有的点隶属变化了，需重新计算（因为质心与本族内所有点的计算有关系）
				clusterChanged = True
			clusterAssment[i,:] = minIndex, minDist**2
		print centroids
		for cent in range(k): # 更新质心
			ptsInClust = dataSet[np.nonzero(clusterAssment[:,0].A==cent)[0]]
			centroids[cent,:] = np.mean(ptsInClust, axis=0)
	return centroids, clusterAssment





