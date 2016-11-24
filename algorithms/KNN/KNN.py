#-*-coding=utf-8-*-

#-----------------------
# Named:	kNN
# Created:	2016-07-08
# @Author:	Qianfeng
#-----------------------

import numpy as np
import operator
import math
import os
def createDataSet():
	group = np.array([[1.0,1.1],[1.0,1.0],[0,0],[0,0.1]])
	labels = ['A','A','B','B']
	return group, labels

def classify0(inX, dataSet, labels, k):
	"""
	k-近邻算法(惰性学习法、生成学习法)
	inX是待分类的特征向量
	"""
	dataSetSize = dataSet.shape[0]
	diffMat = np.tile(inX,(dataSetSize,1)) - dataSet
	sqDiffMat = pow(diffMat, 2)
	sqDistances = sqDiffMat.sum(axis=1)
	distances = np.sqrt(sqDistances)
	sortedDistIndicies = distances.argsort()
	classCount = {}
	for i in range(k):
		voteIlabel = labels[sortedDistIndicies[i]]
		classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1
	sortedClassCount = sorted(classCount.iteritems(),key=operator.itemgetter(1),reverse=True)
	return sortedClassCount[0][0]


# 改进约会网站配对效果（任务分类）
def file2matrix(filename):
	with open(filename) as fr:
		arrayOLines = fr.readlines()
		numberOfLines = len(arrayOLines)
		returnMat = np.zeros((numberOfLines,3))
		classLabelVector = []
		index = 0
		for line in arrayOLines:
			line = line.strip()
			listFromLine = line.split('\t')
			returnMat[index,:] = listFromLine[0:3]
			classLabelVector.append(int(listFromLine[-1]))
			index += 1
	return returnMat, classLabelVector

def autoNorm(dataSet):
	minVals = dataSet.min(0)
	maxVals = dataSet.max(0)
	ranges = maxVals - minVals
	normDataSet = np.zeros(np.shape(dataSet))
	m = dataSet.shape[0]
	normDataSet = dataSet - np.tile(minVals, (m,1))
	normDataSet = normDataSet / np.tile(ranges, (m,1))
	return normDataSet, ranges, minVals

def datingClassTest():
	hoRatio = 0.10
	classifierResult = []
	datingDataMat, datingLabels = file2matrix('D:\\tmp\\datingTestSet2.txt')
	normMat, ranges, minVals = autoNorm(datingDataMat)
	m = normMat.shape[0]
	numTestVecs = int(m*hoRatio)
	errorCount = 0.0
	for i in range(numTestVecs):
		classifierResult = classify0(normMat[i,:], normMat[numTestVecs:m,:],datingLabels[numTestVecs:m],3)
		if (classifierResult != datingLabels[i]): errorCount += 1.0
	print 'the total accurace rate is: %f' % (1-errorCount / float(numTestVecs))

#---------------------------------------------
# knn实现手写识别系统
def img2vector(filename):
	"""
	对单个文件进行转换
	"""
	returnVect = np.zeros((1,1024))
	with open(filename) as fr:
		for i in range(32):
			lineStr = fr.readline()
			for j in range(32):
				returnVect[0,32*i+j] = int(lineStr[j])
	return returnVect

# 使用 knn 算法识别手写数字
def handwritingClassTest(k=3):
	hwLabels = []
	trainingFileList = os.listdir('E:\\test\\trainingDigits')
	m = len(trainingFileList)
	trainingMat = np.zeros((m,1024))
	for i in range(m):
		fileName = trainingFileList[i]
		fileStr = fileName.split('.')[0]
		classNumStr = int(fileStr.split('_')[0])
		hwLabels.append(classNumStr)
		trainingMat[i,:] = img2vector('E:\\test\\trainingDigits\\%s' % fileName)
	testFileList = os.listdir('E:\\test\\testDigits')
	errorCount = 0.0
	mTest = len(testFileList)
	for i in range(mTest):
		fileName = testFileList[i]
		fileStr = fileName.split('.')[0]
		classNumStr = int(fileStr.split('_')[0])
		vectorUnderTest = img2vector('E:\\test\\testDigits\\%s' % fileName)
		classifierResult = classify0(vectorUnderTest, trainingMat, hwLabels, k)
		# print 'came back with: %d, the real answer is: %d' % (classifierResult,classNumStr)
		if(classifierResult != classNumStr):
			errorCount += 1.0
	print "\nthe total number of errors is: %d" % errorCount
	print 'The total accurace rate is: %f' % (1-errorCount/float(mTest))





