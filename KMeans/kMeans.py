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

def distEclud(vecA, vecB):
	return np.sqrt(np.sum(np.power(vecA - vecB, 2)))


def randCent(dataSet, k):
	n = np.shape(dataSet)[1]
	centroids = np.mat(np.zeros((k,n)))
	for j in range(n): # 随机初始化质心
		minJ = np.min(dataSet[:,j])
		rangeJ = float(np.max(dataSet[:,j]) - minJ)
		centroids[:,j] = minJ + rangeJ * np.random.rand(k,1) # 每次初始化所有质心的一个特征列
	return centroids

#------------------------------------------

def kMeans(dataSet, k, distMeas=distEclud, createCent=randCent):
	m = np.shape(dataSet)[0]
	clusterAssment = np.mat(np.zeros((m,2))) # 存放每个点的标签
	centroids = createCent(dataSet, k)
	clusterChanged = True
	while clusterChanged: # 循环迭代更新质心，直到所有点的隶属不在变化
		clusterChanged = False
		for i in range(m): # 对所有点计算与各质心距离，划分隶属
			minDist = np.inf
			minIndex = -1
			for j in range(k): # 遍历质心，计算距离，确定点的隶属族
				distJI = distMeas(centroids[j,:], dataSet[i,:])
				if distJI < minDist:
					minDist = distJI
					minIndex = j
			if clusterAssment[i,0] != minIndex: # 有的点隶属变化了，需重新计算（因为质心与本族内所有点的计算有关系）
				clusterChanged = True
			clusterAssment[i,:] = minIndex, minDist**2
		# print centroids
		for cent in range(k): # 更新质心
			# 获取各族中点的索引
			ptsInClust = dataSet[np.nonzero(clusterAssment[:,0].A==cent)[0]] # 使用索引比对
			centroids[cent,:] = np.mean(ptsInClust, axis=0)
	return centroids, clusterAssment


# 二分K-Means
def biKmeans(dataSet, k, distMeas=distEclud):
	m = np.shape(dataSet)[0]
	clusterAssment = np.mat(np.zeros((m,2)))
	centroid0 = np.mean(dataSet, axis=0).tolist()[0] # 创建初始单个族
	centList = [centroid0]
	for j in range(m): # 计算所有点与族质心的距离
		clusterAssment[j,1] = distMeas(np.mat(centroid0), dataSet[j,:])**2
	while (len(centList) < k): # 是否达到指定的族数 k
		lowestSSE = np.inf
		for i in range(len(centList)): # 尝试划分每一族
			ptsInCurrCluster = dataSet[np.nonzero(clusterAssment[:,0].A==i)[0],:] # 获取此族内所有样本
			centroidMat, splitClustAss = kMeans(ptsInCurrCluster, 2, distMeas)
			# 计算切分之后的 sse
			sseSplit = np.sum(splitClustAss[:,1])
			sseNotSplit = np.sum(clusterAssment[np.nonzero(clusterAssment[:,0].A!=i)[0],1])
			print 'sseSplit, and notSplit: ', sseSplit, sseNotSplit

			if (sseSplit + sseNotSplit) < lowestSSE:
				bestCentToSplit = i # i 是用于切分的族
				bestNewCents = centroidMat
				bestClustAss = splitClustAss.copy()
				lowestSSE = sseSplit + sseNotSplit

		# 更新分配结果（bestClustAss中只有两个族的信息，因为每次是二分）
		bestClustAss[np.nonzero(bestClustAss[:,0].A == 1)[0],0] = len(centList)
		bestClustAss[np.nonzero(bestClustAss[:,0].A == 0)[0],0] = bestCentToSplit

		print 'the bestCentToSplit is: ', bestCentToSplit
		print 'the len of bestClustAss is: ', len(bestClustAss)

		centList[bestCentToSplit] = bestNewCents[0,:] # 更新被切分的族
		centList.append(bestNewCents[1,:]) # 添加新的族
		clusterAssment[np.nonzero(clusterAssment[:,0].A == bestCentToSplit)[0],:] = bestClustAss

	# print centList
	return np.mat(centList), clusterAssment



