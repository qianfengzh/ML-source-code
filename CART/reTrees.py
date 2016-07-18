#-*-coding=utf-8-*-

#-----------------------
# Named:	Linear Regression
# Created:	2016-07-16
# @Author:	Qianfeng
#-----------------------



import numpy as np

def loadDataSet(fileName):
	dataMat = []
	fr = open(fileName)
	for line in fr.readlines():
		curLine = line.strip().split('\t')
		flLine = map(float, curLine)
		dataMat.append(flLine)
	return dataMat

def binSplitDataSet(dataSet, feature, value):
	mat0 = dataSet[np.nonzero(dataSet[:, feature] > value)[0], :]
	mat1 = dataSet[np.nonzero(dataSet[:, feature] <= value)[0], :]
	return mat0, mat1

def regLeaf(dataSet):
	return np.mean(dataSet[:,-1])

def regErr(dataSet):
	return np.var(dataSet[:,-1]) * np.shape(dataSet)[0]

def createTree(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
	feat, val = chooseBestSplit(dataSet, leafType, errType, ops)
	if feat == None:
		return val
	retTree = {}
	retTree['spInd'] = feat
	retTree['spVal'] = val
	lSet, rSet = binSplitDataSet(dataSet, feat, val)
	retTree['left'] = createTree(lSet, leafType, errType, ops)
	retTree['right'] = createTree(rSet,leafType, errType, ops)
	return retTree

<<<<<<< HEAD
#------------------------------------------

def regLeaf(dataSet):
	return np.mean(dataSet[:,-1])

def regErr(dataSet):
	return np.var(dataSet[:,-1]) * np.shape(dataSet)[0]

def chooseBestSplit(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
	tolS = ops[0]
	tolN = ops[1]
	if len(set(dataSet[:,-1].T.tolist()[0])) == 1: # label只有一个值
		return None, leafType(dataSet)
	m, n = np.shape(dataSet)
	S = errType(dataSet)
=======



def chooseBestSplit(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)): 
	# ops控制 leaf node最小样本数（即进行划分的样本数控制）
	tolS = ops[0] # 误差阈值
	tolN = ops[1] # 划分最小样本数阈值
	if len(set(dataSet[:,-1].T.tolist()[0])) == 1:
		return None, leafType(dataSet)
	m, n = np.shape(dataSet)
	S = errType(dataSet)
	bestS = np.inf
	bestIndex = 0
	bestValue = 0
	for featIndex in range(n-1):
		for splitVal in set(dataSet[:,featIndex].A[:,0]):
			mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)
			if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):
				# 待划分的样本数过少，直接忽略
				continue
			newS = errType(mat0) + errType(mat1)
			if newS < bestS:
				bestIndex = featIndex
				bestValue = splitVal
				bestS = newS
	if (S - bestS) < tolS: # 误差达到最小误差阈值，可结束划分
		return None, leafType(dataSet)
	mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue)
	if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):
		return None, leafType(dataSet) # 上面只是做了 continue,并没有返回值
	return bestIndex, bestValue
>>>>>>> 0a572896f7379e85b195f03c1151b4c57c2b623d




