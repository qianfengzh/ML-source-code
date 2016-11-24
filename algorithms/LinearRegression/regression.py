#-*-coding=utf-8-*-

#-----------------------
# Named:	Linear Regression
# Created:	2016-07-15
# @Author:	Qianfeng
#-----------------------

import numpy as np

def loadDataSet(fileName):
	numFeat = len(open(fileName).readline().split('\t')) - 1
	datMat = []
	labelMat = []
	fr = open(fileName)
	for line in fr.readlines():
		lineArr = []
		curLine = line.strip().split('\t')
		for i in range(numFeat):
			lineArr.append(float(curLine[i]))
		datMat.append(lineArr)
		labelMat.append(float(curLine[-1]))
	return datMat, labelMat

def standRegres(xArr, yArr):
	xMat = np.mat(xArr)
	yMat = np.mat(yArr).T
	xTx = xMat.T * xMat
	if np.linalg.det(xTx) == 0.0: # 计算 xTx 矩阵的行列式，判定是否可逆
		print 'This matrix is singular, cannot do inverse'
		return
	ws = xTx.I * (xMat.T * yMat)
	return ws
	

# 局部加权线性回归
def lwlr(testPoint, xArr, yArr, k=1.0):
	xMat = np.mat(xArr)
	yMat = np.mat(yArr).T
	m = xMat.shape[0]
	weights = np.mat(np.eye(m))
	for j in range(m): # 高斯公式计算权重
		diffMat = testPoint - xMat[j,:]
		
		weights[j,j] = np.exp(diffMat * diffMat.T/(-2.0 * k**2))
		
	xTx = xMat.T * (weights * xMat)
	if np.linalg.det(xTx) == 0.0:
		print 'This matrix is singular, cannot do inverse'
		return
	print xMat.shape, weights.shape, yMat.shape, k
	print weights[0,0:5]
	ws = xTx.I * (xMat.T * (weights * yMat))
	return testPoint * ws

def lwlrTest(testArr, xArr, yArr, k=1.0):
	m = np.shape(yArr)[0]
	yHat = np.zeros(m)
	for i in range(m):
		yHat[i] = lwlr(testArr[i], xArr, yArr, k)
	return yHat


def rssError(yArr, yHatArr):
	return ((yArr - yHatArr)**2).sum()


# ---------------------
# shrinkage
# 岭回归
def ridgeRegres(xMat, yMat, lam=0.2):
	xTx = xMat.T * xMat
	denom = xTx + np.eye(np.shape(xMat)[1]) * lam
	if np.linalg.det(denom) == 0:
		print 'This matrix is singular, cannot do inverse'
		return
	ws = denom.I * (xMat.T * yMat)

def ridgeTest(xArr, yArr):
	xMat = np.mat(xArr)
	yMat = np.mat(yArr)
	yMean = np.mean(yMat, 0)
	yMat = yMat - yMean
	xMeans = np.mean(xMat, 0)
	xVar = np.var(xMat, 0)
	xMat = (xMat - xMeans) / xVar
	numTestPts =  30 # 使用不同lam值计算，寻找最佳lam值
	wMat = np.zeros((numTestPts, np.shape(xMat)[1]))
	for i in range(numTestPts):
		ws = ridgeRegres(xMat, yMat, np.exp(i-10))
		wMat[i,:] = ws.T
	return wMat


# 向前逐步线性回归
def stageWise(xArr, yArr, eps=0.01, numIt=100): # eps 为每次迭代调整的步长
	xMat = np.mat(xArr)
	yMat = np.mat(yArr).T
	yMean = np.mean(yMat, 0)
	yMat = yMat - yMean
	xMean = np.mean(xMat, 0)
	xVar = np.var(xMat, 0)
	xMat = (xMat - xMean) / xVar
	m, n = np.shape(xMat)
	returnMat = np.zeros((numIt, n))
	ws = np.zeros((n, 1))
	wsTest = ws.copy()
	wsMax = ws.copy()
	for i in range(numIt): # 整个权重更新迭代次数
		print ws.T
		lowestError = inf
		for j in range(n): # 对每个特征
			for sign in [-1, 1]: # 对每个特征（增加减少此特征，观察误差）
				wsTest = ws.copy()
				wsTest[j] += eps * sign
				yTest = xMat * wsTest
				rssE = rssError(yMat.A, yTest.A)
				if rssE < lowestError:
					lowestError = rssE
					wsMax = wsTest
		ws = wsTest.copy()
		returnMat[i,:] = ws.T
	return returnMat





