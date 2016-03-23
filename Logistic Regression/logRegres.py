#coding=utf-8
'''
Named:    Logistic Regression
Created:  2016/03/23
@Author:  Qian Feng
'''

import numpy as np
import math
import operator
import matplotlib.pyplot as plt
import random

# handle the train dataSet
def loadDataSet():
	dataMat = []
	labelMat = []
	with open('testSet.txt') as fr:
		for line in fr.readlines():
			lineArr = line.strip().split()
			dataMat.append([1.0, float(lineArr[0]),float(lineArr[1])])
			labelMat.append(int(lineArr[2])) # list
	return dataMat, labelMat

# create a sigmoid function to handle a vector
def sigmoid(inX):
	return 1.0/(1 + math.exp(-inX))

# using the gradient ascend algorithm
def gradAscent(dataMatIn, classLabels):
	dataMatrix = np.mat(dataMatIn)
	labelMat = np.mat(classLabels).transpose() # transform the label list to a rank vector
	m, n = np.shape(dataMatrix)  # m is the number of train data vector,and the n is the viriable
	alpha = 0.01
	maxCycles = 500
	weigths = np.ones((n,1))  # weigths is a rank vector of parameters,and the n is the number of parameter
	for k in range(maxCycles):
		h = sigmoid(dataMatrix * weigth) # h is a value-vactor which from the hypothetive fuction calculated
		error = (labelMat - h)
		# from here,the gradiant function is the optimized function's derivative by using the least square method
		weigths = weigths + alpha * dataMatrix.transpose()*error
	return weigths # matrix type

#######################

# 画出数据集和 Logistic回归的最佳拟合直线
# Parameters:
#	wei:  matrix
def plotBestFit(wei):
	weigths = wei.getA() # return the matrix self by ndarray type
	dataMat, labelMat = loadDataSet()
	dataArr = np.array(dataMat)
	m = np.shape(dataArr)[0]
	xcord1 = []
	ycord1 = []
	xcord2 = []
	ycord2 = []
	for i in range(m):
		if int(labelMat[i]) == 1:
			xcord1.append(dataArr[i,1])
			ycord1.append(dataArr[i,2])
		else:
			xcord1.append(dataArr[i,1])
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


#####################################

# random gradient ascending algorithm
def stocGradAscent0(dataMatrix, classLabels):
	m, n = np.shape(dataMatrix)
	alpha = 0.01
	weigths = np.ones(n)
	for i in range(m):  # 只对整个数据集迭代了一次，上面的方法对整个数据集迭代了500次
		h = sigmoid(sum(dataMatrix[i]*weigths))
		error = classLabels[i] - h  # both h and error are value
		weigths = weigths + alpha * error * dataMatrix[i]
	return weigths  # 1 x N

# improvment of random gradient ascending algorithm
def stocGradAscent1(dataMatrix, classLabels, numIter=150):
	m, n = np.shape(dataMatrix)
	weigths = np.ones(n)
	for j in range(numIter):
		dataIndex = range(m)
		for i in range(m):
			# 常数项 0.01 是为了保证在多次迭代后，进来的新数据任然具有一定的影响力
			# 若要处理的问题是动态变化的，可以适当加大常数项
			# j << max(i) 时，alpha就不是严格下降的
			alpha = 4/(1.0+j+i)+0.01   # alpha 每次迭代时需要调整（即收敛速度先快后慢）### 会缓解数据波动或高频波动
			randIndex = int(random.uniform(0,len(dataIndex)))  # 随机选取更新（可以减少周期性的波动）
			h = sigmoid(sum(dataMatrix[randIndex]*weigths))
			error = classLabels[randIndex] - h
			weigths = weigths + alpha * error * dataMatrix[randIndex]
			del(dataMatrix[randIndex]) # 每次随机选取数据，故此处需将选取过的数据进行删除
	return weigths

####################################
#    Algorithm Testing
####################################
def classifyVector(inX, weigths):
	prob = sigmoid(sum(imX * weigths))
	if prob > 0.5:
		return 1.0
	else:
		return 0.0

def colicTest():
	trainingSet = []
	trainingLabels = []
	with open('horseColictraining.txt') as frTrain:
		for line in frTrain.readlines():
			currLine = line.strip().split('\t')
			lineArr = []
			for i in range(21):
				lineArr.append(float(currLine[i]))
			trainingSet.append(lineArr)
			trainingLabels.append(float(currLine[21]))
		trainWeigths = stocGradAscent1(np.array(trainingSet), trainingLabels, 500)
	
	errorCount = 0
	numTestVec = 0.0
	with open('horseColicTest.txt') as frTest:
		for line in frTest.readlines():
			numTestVec += 1.0
			currLine = line.strip().split('\t')
			lineArr = []
			for i in range(21):
				lineArr.append(float(currLine[i]))
			if int(classifyVector(np.array(lineArr), trainWeigths)) != int(currLine[21]):
				errorCount += 1
	errorRate = (float(errorCount)/numTestVec)
	print "the error rate of this test is: %f" % errorRate
	return errorRate

def multiTest():
	numTests = 10
	errorSum = 0.0
	for k in range(numTests):
		errorSum += colicTest()
	print "after %d iterations the average error rate is: %f" % (numTests, errorSum/float(numTests))



