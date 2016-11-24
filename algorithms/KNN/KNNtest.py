#coding=utf-8
import os
import operator
import numpy as np

# make a test dataset
def createDataSet():
	group = np.array([1.0,1.0],[1,1.1],[0,0][0.1,0])
	labels = ['A','A','B','B']
	return group,labels
# classify function
def classify(inX,trainData,lavels,k):
	"""
	1) 计算距离，并排序
	2）找到k个临近的label，对各label计数
	3）排序，取频度最大的label
	"""
	trainDataSize = len(trainData[0])
	diffMat = np.tile(inX,(trainData,1)) - trainData
	sqDiffMat = diffMat ** 2
	sqDiffMat = sqDiffMat.sum(1)
	distinces = sqDiffMat ** 0.5
	sortDistance = distinces.argsort()
	labelCount = {}
	for i in k:
		label = labels[sortDistance[i]]
		labelCount[label] = labelCount.get(label,0) + 1
	sortedLabelCount = sorted(labelCount.iteritems(),operator.itemgetter(1),reverse = True)
	return sortedLabelCount[0][0]
##########################################
# Make a decision for dating by KNN algorithm

# Obtain the dataSet
def file2matrix(filename):
	with open(filename) as fl:
		arrayLines = fl.readlines()
	arraySize = len(arrayLines)
	dataSet = np.zeros(arraySize,3)
	labelVec = []
	for i in range(arraySize):
		dataSetList = arrayLines[i].strip.split('\t')
		dataSet[i] = dataSetList[:3]
		labelVec.append(dataSetList[-1])
	return dataSet, labelVec

