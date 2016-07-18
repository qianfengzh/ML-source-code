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
		flLine = np.map(float, curLine)
		dataMat.append(flLine)
	return dataMat

def binSplitDataSet(dataSet, feature, value):
	mat0 = dataSet[np.nonzero(dataSet[:, feature] > value)[0], :]
	mat1 = dataSet[np.nonzero(dataSet[:, feature] <= value)[0], :]
	return mat0, mat1


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




