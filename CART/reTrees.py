#-*-coding=utf-8-*-

#-----------------------
# Named:	Linear Regression
# Created:	2016-07-16
# @Author:	Qianfeng
#-----------------------



import numpy as np
from numpy import linalg as la

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


# =====================================
# 对树进行后剪枝
def isTree(obj):
	return (type(obj).__name__=='dict')

def getMean(tree):
	if isTree(tree['right']):
		tree['right'] = getMean(tree['right'])
	if isTree(tree['left']):
		tree['left'] = getMean(tree['left'])
	return (tree['left'] + tree['right']) / 2.0

def prune(tree, testData):
	if np.shape(testData)[0] == 0: # 没有测试数据则对树进行塌陷处理
		return getMean(tree)
	if (isTree(tree['right']) or isTree(tree['left'])): # 切分数据集，寻找树叶
		lSet, rSet = binSplitDataSet(testData, tree['spInd'], tree['spVal'])
	if isTree(tree['left']): # 左树递归
		tree['left'] = prune(tree['left'], lSet)
	if isTree(tree['right']): # 右树递归
		tree['right'] = prune(tree['left'], lSet)
	if not isTree(tree['left']) and not isTree(tree['right']): # 从叶节点的第一个父节点回溯
		lSet, rSet = binSplitDataSet(testData, tree['spInd'], tree['spVal'])
		errorNoMerge = np.sum(np.power(lSet[:,-1] - tree['left'],2)) +\
			np.sum(np.power(rSet[:,-1] - tree['right'],2))
		treeMean = (tree['left'] + tree['right']) / 2.0
		errorMerge = np.sum(np.power(testData[:,-1] - treeMean,2))
		if errorMerge < errorNoMerge:
			print 'merging'
			return treeMean
		else:
			return tree
	else:
		return tree



#================================================
# 回归模型树

def linearSolve(dataSet):
	m,n = np.shape(dataSet)
	X = np.mat(np.ones((m,n)))
	Y = np.mat(np.ones((m,1)))
	X[:,1:n] = dataSet[:,0:n-1]
	Y = dataSet[:,-1]
	xTx = X.T * X
	if la.det(xTx) = 0.0:
		raise NameError('This matrix is singular, cannot do inverse,\n\
			try increasing the second value of ops.')
	ws = xTx.I * (X.T * Y)
	return ws, X, Y

def modelLeaf(dataSet):
	ws, X, Y = linearSolve(dataSet)
	return ws

def modelErr(dataSet):
	ws, X, Y = linearSolve(dataSet)
	yHat = X * ws
	return np.sum(np.power(Y - yHat, 2))




# ---======================
# 树回归预测

def regTreeEval(model, inDat):
	return float(model)

def modelTreeEval(model, inDat):
	n = np.shape(inDat)[1]
	X = np.mat(np.ones((1, n+1)))
	X[:,1:n+1] = inDat
	return flaot(X * model)

def treeForecast(tree, inData, modelEval=regTreeEval):
	if not isTree(tree):
		return modelEval(tree, inData)
	if inData[tree['spInd']] > tree['spVal']:
		if isTree(tree['left']):
			return treeForecast[tree['left'], inData, modelEval]
		else:
			return modelEval(tree['left'], inData)
	else:
		if isTree(Tree['right']):
			return treeForecast[tree['right'], inData, modelEval]
		else:
			return modelEval(tree['right'], inData)

def createForeCast(tree, testData, modelEval=regTreeEval):
	m = len(testData)
	yHat = np.mat(np.zeros((m,1)))
	for i in range(m):
		yHat[i,0] = treeForecast(tree, np.mat(testData[i]), modelEval)
	return yHat











