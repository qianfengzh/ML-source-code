#coding = utf-8
"""
Named:   KNN algorithm
Created: 2016/03/03
Author:  Qian Feng
"""
from numpy import *
import operator
import os
###############################################
#Simple example
#create a simple dataset
def createDataSet():
	group = array([1.0,1.1],[1.0,1.0],[0,0],[0,0.1])
	labels = ['A','A','B','B']
	return group,labels

#classify by KNN algorithm
"""
Parameter:
	inX: vector which waiting for classifying
	dataSet: trainDataSet
	labels: the vector of labels,sharing indexes with dataSet
	k: the number of neibhgourhood
Return:
	the minimun distance label
"""
def classify0(inX,dataSet,labels, k):
	#obtain the row dimenssion of trainDataSet
	dataSetSize = dataSet.shape[0]
	#1)obtian the distance
	diffMat = tile(inX, (dataSetSize,1)) - dataSet
	sqDistances = diffMat**2
	sqDistances = sqDistances.sum(axis=1)
	distances = sqDistances**0.5
	#2)sorting by distiance
	sorteDistIndicies = distances.argsort()
	#3)choose k point that has minimum distance
	classCount = {}
	for i in range(k):
		voteIlabel = labels[sorteDistIndicies[i]] #dataSet and labels have share the index
		classCount[voteIlabel] = classCount.get(voteIlabel,0) +1
	#4)sorting by frequence
	sortedClassCount = sorted(classCount.iteritems(),
		key = operator.itemgetter(1),reverse = True)
	#5)obtain the label with maximum frequence
	return sortedClassCount[0][0]
########################################################

########################################################
#Dating 
#Transform the text file to matrix
"""
Input: text file
Output: traintDataSet and labels
"""
def file2matrix(filename):
	with open(filename) as fr:
		arrayLines = fr.readlines()
	numberOfLines = len(arrayLines)
	returnMat = zeros((numberOfLines,3))
	classLabelVector = []
	index = 0
	for line in arrayLines:
		line = line.strip()
		listFormLine = line.split('\t')
		returnMat[index,:] = listFormLine[0:3]
		classLabelVector.append(int(listFormLine[-1]))
		index += 1
	return returnMat,classLabelVector

#normalizing (normalValue = (Value-min)/(max-min))
"""
Input: dataSet that needs to normalizing
Return: normalized, ranges(defined by max-min),minimum Value
"""
def autoNorm(dataSet):
	minVals = dataSet.min(0)
	maxVals = dataSet.max(0)
	ranges = maxVals - minVals
	normDataSet = zeros(shape(dataSet))
	m = dateSet.shape[0]
	normDataSet = dataSet - tile(minVals, (m,1))
	normDataSet = normDataSet/tile(ranges, (m,1))
	return normDataSet, ranges, minVals

#dating data testing
#### Note that: There user a dataSet as both train data and test data!
def datingClassTest(testFileName):
	hoRatio = 0.10   # hold out 10% to predict and leave 90% as the trainSet 
	#import testData and normalizing
	datingDataMat,datingLabels = file2matrix(testFileName)
	normMat, ranges, minVals = autoNorm(datingDataMat)
	m = normMat.shape[0]
	numTestVecs = int(m*hoRatio)
	errorCount = 0.0
	for i in range(numTestVecs):
		classifierResult = classify0(normMat[i,:],normMat[numTestVecs:m,:],\
			datingLabels[numTestVecs:m], 3)
		print "The classifier came back with: %d, the real answer is: %d"\
					% (classifierResult, datingLabels[i])
		if (classifierResult != datingLabels[i]):errorCount += 1.0
	print "The total error rate is: %f" % (errorCount/float(numTestVecs))
####################################################3

####################################################
# 手写识别系统
# Transform img to vector
"""
# Input the binary img
# Output the vector
"""
def img2vector(filename):
	returnVect = zeros((1,1024))
	with open(filename) as fr:
		for i in range(32):
			lineStr = fr.readline()
			for j in range(32):
				returnVect[0,32*i+j] = int[lineStr[j]]
	return returnVect

# Test code
def handwritingClassTest(trainingDigitsFile,testDigitsFile):
	hwLabels = []
	trainingFileList = os.listdir(trainingDigitsFile)
	m = len(trainingFileList)
	trainingMat = zeros((m,1024))
	# obtain the train data and their labels
	for i in range(m):
		fileNameStr = trainingFileList[i]
		fileStr = fileNameStr.split('.')[0]
		classNumStr = int(fileStr.split('_')[0])
		hwLabels.append(classNumStr)
		trainingMat[i,:] = img2vector(trainingDigitsFile+'\\'+fileNameStr)
	testFileList = od.listdir(testDigitsFile)
	errorCount = 0.0
	mTest = len(testFileList)
	for i in range(mTest):
		fileNameStr = testFileList[i]
		fileStr = fileNameStr.split('.')[0]
		classNumStr = int(fileStr.split('_')[0])
		vectorUnderTest = img2vector(testDigitsFile+'\\'+fileNameStr)
		classifierResult = classify0(vectorUnderTest,\
			trainingMat,hwLabels, 3)
		print "the classifier came back with: %d, the real answer is: %d"\
		% (classifierResult, classNumStr)
		if (classifierResult != classNumStr): errorCount += 1.0
	print "\nthe total number of errors is: %d" % errorCount
	print "\nthe total error rate is: %f" % (errorCount/float(mTest))


