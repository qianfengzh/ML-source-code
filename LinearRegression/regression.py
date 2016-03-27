#coding=utf-8
"""
Named:   Linear Regression
Created: 2016/03/26
@Author: Qian Feng
"""

import numpy as np
from time import sleep
import json
import urllib2

def  loadDataSet(fileName='F:\\Git\ML-source-code\\LinearRegression\\ex0.txt'):
	with open(fileName) as fr:
		numFeat = len(fr.readline().split('\t')) - 1
		dataMat = []; labelMat = []
		for line in fr.readlines():
			lineArr = []
			curline = line.strip().split('\t')  # 除掉每行行末的换行符
			for i in range(numFeat):
				lineArr.append(float(curline[i]))
			dataMat.append(lineArr)
			labelMat.append(float(curline[-1]))
	return dataMat, labelMat


# 最佳拟合直线方法（可能会出现欠拟合现象）
def standRegres(xArr, yArr):
	xMat = np.mat(xArr); yMat = np.mat(yArr).T
	xTx = xMat.T * xMat
	if np.linalg.det(xTx) == 0.0:  # 计算矩阵的行列式，判断矩阵是否可逆
		print "This matrix is singular, cannot do inverse"
		return
	ws = xTx.I * (xMat.T * yMat)
	return ws

# LWLR: 局部加权线性回归
def lwlr(testpoint, xArr, yArr, k=1.0):
	xMat = np.mat(xArr); yMat = np.mat(yArr).T
	m = np.shape(xMat)[0]
	weigths = np.mat(np.eyes(m))
	for j in range(m):
		diffMat = testpoint - xMat[j,:]
		weigths[j,j] = exp(diffMat * diffMat.T/(-2.0*k**2))
	xTx = xMat.T * (weigths * xMat)
	if np.linalg.det(xTx) == 0.0:
		print " This matrix is singular, cannot do inverse"
		return
	ws = xTx.I * (xMat.T * (weigths * yMat)))
	return testpoint * ws

def lwlrTest(testArr, xArr, yArr, k=1.0):
	m = np.shape(testArr)[0]
	yHat = np.zeros(m)
	for i in range(m):
		yHat[i] = lwlr(testArr[i], xArr, yArr, k)
	return

def rssError(yArr, yHatArr): # 分析预测误差的大小
	return ((yArr - yHatArr) ** 2).sum()



# 岭回归
def ridgeRegres(xMat, yMat, lam=0.2):
	xTx = xMat.T * xMat
	denom = xTx + np.eye(np.shape(xMat)[1]) * lam
	if np.linalg.det(denom) == 0.0:
		print "This matrix is singular, cannot do inverse"
		return
	ws = denom.I * (xMat.T * yMat)
	return ws

def ridgeTest(xArr, yArr):
	xMat = np.mat(xArr);  yMat = np.mat(yArr).T
	# 数据标准化
	yMean = np.mean(yMean, 0)
	yMat = yMat -yMean
	xMeans = np.mean(xMat, 0)
	xVar = np.var(xMat, 0)
	xMat = (xMat - xMeans)/xVar
	numTestPts = 30
	wMat = np.zeros((numTestPts.shape(xMat)[1]))
	for i in range(numTestPts):
		ws = ridgeRegres(xMat, yMat, exp(i-10))
		wMat[i,:] = ws.T
	return wMat


# lasso 简单实现： 向前逐步回归
# eps 是每次迭代需要调整的步长，numIt 是迭代次数
def stageWise(xArr, yArr, eps=0.01, numIt=100):
	xMat = np.mat(xArr); yMat = np.mat(yArr).T
	yMean = np.mean(yMat,0)
	yMat = yMat - yMean
	xVar = np.var(xMat, 0)
	xMat = (xMat - xMeans)/xVar
	m, n = np.shape(xMat)
	returnMat = np.zeros((numIt, n))
	ws = np.zeros((n,1)); wsTest = ws.copy(); wsMax = ws.copy()
	for i in range(numIt):
		print ws.T
		lowestError = np.inf   # 初始值设为正无穷
		for j in range(n):
			for sign in [-1,1]: # 在每个特征上运行两次for循环，分别计算增加或减少该特征对误差的影响
				wsTest = ws.copy()
				wsTest[j] += eps * sign
				yTest = xMat * wsTest
				rssE = rssError[yMat.A, yTest.A]
				if rssE < lowestError:
					lowestError = rssE
					wsMax = wsTest
		ws = wsMax.copy()
		returnMat[i,:] = ws.T
	return returnMat



# 预测乐高玩具套装价格
def searchForSet(retX, retY, setNum, yr, numPce, origPrc):
	sleep(10)
	myAPIstr = 'get from code.google.com'
	searchURL = 'https://www.googleapis.com/shopping/search/v1/public/products?\
	key=%s&country=US$q=lego+%d&alt=json' % (myAPIstr, setNum)
	pg = urllib2.urlopen(searchURL)
	retDict = json.loads(pg.read())
	for i in range(len(retDict['time'])):
		try:
			currItem = retDict['time'][i]
			if currItem['product']['condition'] == 'new':
				newFlag = 1
			else:
				newFlag = 0
			listOfInv = currItem['product']['inventories']
			for item in listOfInv:
				sellingPrice = item['price']
				if sellingPrice > origPrc * 0.5:  # 过滤掉不完整的套装
					print "%d\t%d\t%d\t%f\t%f" % (yr, numPce, newFlag, origPrc, sellingPrice)
					retX.append([yr, numPce, newFlag, origPrc])
					retY.append(sellingPrice)
		except:
			print 'problem with item %d' % i

def setDataCollect(retX, retY):
	pass


# 交叉验证测试岭回归、缩减法确定最佳回归系数
def crossValidation(xArr, yArr, numVal=10):
	m = len(yArr)
	indexList = range(m)
	errorMat = np.zeros((numVal,30))
	for i in range(numVal):
		trainX = []; trainY =[]
		testX = []; testY = []
		random.shuffle(indexList)
		for j in range(m):
			if j < m * 0.9:
				trainX.append(xArr[indexList[j]])
				trainY.append(yArr[indexList[j]])
			else:
				testX.append(xArr[indexList[j]])
				testY.append(yArr[indexList[j]])
		wMat = ridgeTest(trainX, trainY)  # 使用岭回归
		for k in range(30):  # 用训练时的参数将测试数据标准化
			matTestX = np.mat(testX); matTrainX = np.mat(trainX)
			meanTrain = np.mean(matTrainX, 0)
			varTrain = np.var(matTrainX, 0)
			matTestX = (matTestX - meanTrain)/varTrain
			yEst = matTestX * np.mat(wMat[k,:].T + np.mean(trainY))
			errorMat[i,k] = rssError(yEst.T.A, np.array(testY))
	meanErrors = np.mean(errorMat, 0)
	minMean = float(min(meanErrors))
	bestWeights = wMat[np.nonzero(meanErrors = minMean)]
	xMat = np.mat(xArr); yMat = np.mat(yArr).T
	meanX = np.mean(xMat, 0); varX = np.var(xMat, 0)
	unReg = bestWeights/varX
	print "the best model from Ridge Regression is:\n",unReg
	print "with constant term: ",-1 * sum(np.multiply(meanX,unReg)) + np.mean(yMat)

