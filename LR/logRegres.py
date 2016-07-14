#-*-coding=utf-8-*-

#-----------------------
# Named:	Logistic Regression
# Created:	2016-07-12
# @Author:	Qianfeng
#-----------------------

import numpy as np
import random
import matplotlib.pyplot as plt

def loadDataSet():
	dataMat = []
	labelMat = []
	with open('testSet.txt') as fr:
		for line in fr.readlines():
			lineArr = line.strip().split()
			dataMat.append([1.0, float(lineArr[0]), float(lineArr[1])])
			labelMat.append(int(lineArr[2]))
	return dataMat, labelMat

def sigmoid(inX):
	return 1.0/(1+np.exp(-inX))

def gradAscent(dataMatIn, classLabels):
	dataMatrix = np.mat(dataMatIn)
	labelMat = np.mat(classLabels).transpose()
	m, n = np.shape(dataMatrix)
	alpha = 0.001 # learning rate
	maxCycle = 500 # stop condition
	weigths = np.ones((n,1))
	for k in range(maxCycle):
		h = sigmoid(dataMatrix * weigths)
		# 梯度上升更新
		error = (labelMat - h)
		weigths = weigths + alpha * dataMatrix.transpose() * error
	return weigths

#----------------------------------------------------------------

def plotBestFit(weigths):
	dataMat, labelMat = loadDataSet()
	dataArr =  np.array(dataMat)
	n = dataArr.shape[0]
	xcord1 = []; ycord1 = []
	xcord2 = []; ycord2 = []
	for i in range(n):
		if int(labelMat[i]) == 1:
			xcord1.append(dataArr[i,1])
			ycord1.append(dataArr[i,2])
		else:
			xcord2.append(dataArr[i,1])
			ycord2.append(dataArr[i,2])
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.scatter(xcord1, ycord1, s=30, c='red', marker='s')
	ax.scatter(xcord2, ycord2, s=30, c='green')
	x = np.arange(-3.0, 3.0, 0.1)
	y = (-weigths[0]-weigths[1]*x)/weigths[2]
	ax.plot(x, y)
	plt.xlabel('X1')
	plt.ylabel('X2')
	plt.show()


#----------------------------------------------
# 随机梯度上升（可用作在线学习）

def stocGradAscent0(dataMatrix, classLabels):
	m, n = dataMatrix.shape
	alpha = 0.01
	weigths = np.ones((n,1))
	for i in range(m): # 对 m 个样本进行逐个迭代
		h = sigmoid(sum(dataMatrix[i] * weigths))
		error = classLabels[i] - h
		weigths = weigths + alpha * error * dataMatrix[i]

	return weigths

def stocGradAscent1(dataMatrix, classLabels, numIter=150):
	m, n = dataMatrix.shape
	weigths = np.ones(n)
	for j in range(numIter):
		dataIndex = range(m)
		for i in range(m):
			alpha = 4/(1.0+j+i)+0.01 # alpha 的衰减速度先快后慢
			randIndex = int(random.uniform(0,len(dataIndex)))
			h = sigmoid(sum(dataMatrix[randIndex] * weigths))
			error = classLabels[randIndex] - h
			weigths = weigths + alpha * error * dataMatrix[randIndex]
			del (dataMatrix[randIndex])
	return weigths


#---------------------------------------------------
# 实际应用

def classifyVector(inX, weigths):
	prob = sigmoid(sum(inX * weigths))
	if prob > 0.5:
		return 1.0
	else: return 0.0

def colicTest():
	frTrain = open('horseColicTraining.txt')
	frTest = open('horseColicTest.txt')
	trainingSet = []
	trainingLabels = []
	for line in frTrain.readlines():
		currLine = line.strip().split('\t')
		lineArr = []
		for i in range(21):
			lineArr.append(float(currLine[i]))
		trainingSet.append(lineArr)
		trainingLabels.append(float(currLine[i]))
	trainWeights = stocGradAscent1(np.array(trainingSet), trainingLabels, 500)
	errorCount = 0.0
	numTestVec = 0.0
	for line in frTest.readlines():
		numTestVec += 1.0
		currLine = line.strip().split('\t')
		lineArr = []
		for i in range(21):
			lineArr.append(float(currLine[i]))
		if int(classifyVector(np.array(lineArr), trainWeights))!=int(currLine[21]):
			errorCount += 1.0
	errorRate = (float(errorCount)/numTestVec)
	return errorRate

def multiTest():
	numTestVec = 10
	errorSum = 0.0
	for k in range(numTests):
		errorSum += colicTest()
	return errorSum/float(numTests)





