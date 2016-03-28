#coding=utf-8
"""
Named:   Classification And Regression Trees
Created: 2016/03/28
@Author: Qian Feng
"""

'''
回归树构思：
	1、寻找最佳切分特征；
		1> 对每个特征的每个特征值；
		2> 将数据据集切分成两份，计算切分误差；
		3> 若当前误差小于最小误差，将当前切分设定为最佳切分并更新最小误差；
		4> 返回最佳切分的特征和阈值。
	2、页节点判断，即若不能再分，将该节点保存为叶节点；
	3、进行二元切分；
	4、对左、右子树进行迭代建树
'''

import numpy as np


def loadDataSet(fileName):
	dataMat = []
	with open(fileName) as fr:
		for line in fr.readlines():
			curLine = line.strip().split('\t')
			fltLine = map(float,curLine)
			dataMat.append(fltLine)
	return dataMat  # the dataMat contains both trainData and labelData


def binSplitDataSet(dataSet, feature, value):
	mat0 = dataSet[np.nonzero(dataSet[:,feature] > value)[0],:]
	mat1 = dataSet[np.nonzero(dataSet[:,feature] <= value)[0],:]
	return mat0, mat1


def regLeaf(dataSet):
	return np.mean(dataSet[:,-1])

def regErr(dataSet):
	return np.var(dataSet[:,-1]) * np.shape(dataSet)[0]   # total var error

def chooseBestSplit(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
	tolS = ops[0]; tolN = ops[1]
	if len(set(dataSet[:,-1].T.tolist()[0])) == 1:  # return while all value was equal
		return None, leafType(dataSet)

	m, n = np.shape(dataSet)
	S = errType(dataSet)
	dataSet = dataSet.A
	bestS = np.inf; bestIndex = 0; bestValue = 0
	for featIndex in range(n-1):
		for splitVal in set(dataSet[:,featIndex]):
			mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)
			if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN):
				continue

			newS = errType(mat0) + errType(mat1)
			if newS < bestS:
				bestIndex = featIndex
				bestValue = splitVal
				bestS = newS
	if (S - bestS) < tolS:  # return while the error to small
		return None, leafType(dataSet)

	mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue)
	if (np.shape(mat0)[0] < tolN) or (np.shape(mat1)[0] < tolN): # return while the child set was too small
		return None, leafType(dataSet)

	return bestIndex, bestValue



def createTree(dataSet, leafType=regLeaf, errType=regErr, ops=(1,4)):
	'''
	Return a tree dict.
		The module will be the scalar while creating a regression tree or a linear function. 

	Parameters:
	-----------
	dataSet: -->array_like
		Contains the trainData and tha labelData.
	leafType: -->function
		The function which to create the leafNode.
	errType: -->function
		The function which to caculate the error.
	ops: --> tuple
		Parameters of condition for stopping the feature select function.
	'''
	feat, val = chooseBestSplit(dataSet, leafType, errType, ops)
	if feat == None: return val   # return the leafNode value when obtaining the condition

	retTree = {}
	retTree['spInd'] = feat
	retTree['spVal'] = val
	lSet, rSet = binSplitDataSet(dataSet, feat, val)
	retTree['left']  = createTree(lSet, leafType, errType, ops)
	retTree['right'] = createTree(rSet, leafType, errType, ops)
	return retTree




