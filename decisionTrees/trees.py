#-*-coding=utf-8-*-

#-----------------------
# Named:	Decision Tree
# Created:	2016-07-10
# @Author:	Qianfeng
#-----------------------

from math import log
import operator
import pickle
from sklearn.tree import DecisionTreeClassifier

def createDataSet():
	dataSet = [[1,1,'yes'],[1,1,'yes'],[1,0,'no'],[0,1,'no'],[0,1,'no']]
	labels = ['no surfacing', 'flippers']
	return dataSet, labels

def calcShannonEnt(dataSet):
	"""
	计算香农熵
	"""
	numEntries = len(dataSet)
	labelCounts = {}
	for featVect in dataSet:
		currentLabel = featVect[-1]
		labelCounts[currentLabel] = labelCounts.get(currentLabel,0)+1
	shannonEnt = 0.0
	for key in labelCounts:
		prob = float(labelCounts[key])/numEntries
		shannonEnt -= prob * log(prob,2)
	return shannonEnt


def splitDataSet(dataSet, axis, value):
	"""
	将数据按指定轴和指定值进行切分
	"""
	retDataSet = []
	for featVect in dataSet:
		if featVect[axis] == value:
			reducedFeatVec = featVect[:axis]
			reducedFeatVec.extend(featVect[axis+1:])
			retDataSet.append(reducedFeatVec)
	return retDataSet

def chooseBestFeatureToSplit(dataSet):
	"""
	选取最佳划分方式
	"""
	numFeatures = len(dataSet[0]) - 1
	baseEntropy = calcShannonEnt(dataSet)
	bestInfoGain = 0.0; bestFeature = -1
	for i in range(numFeatures):
		featList = [example[i] for example in dataSet]
		uniqueValues = set(featList)
		newEntropy = 0.0
		for value in uniqueValues:
			subDataSet = splitDataSet(dataSet, i, value)
			prob = len(subDataSet)/float(len(dataSet))
			newEntropy += prob * calcShannonEnt(subDataSet)
		infoGain = baseEntropy - newEntropy
		if (infoGain > bestInfoGain):
			bestInfoGain = infoGain
			bestFeature = i
	return bestFeature

def Gini(dataSet):
	giniValue = 0.0
	labelsList = dataSet[-1]
	labelsCount = len(dataSet)
	uniqueValues = set(dataSet[-1])
	for value in uniqueValues:
		giniValue += pow(labelsList.count(value)/float(labelsCount), 2)
	return 1-giniValue


def chooseBestFeatureToSplitByGini(dataSet):
	numFeatures = len(dataSet[0]) - 1
	baseGini = Gini(dataSet)
	bestGiniGain = 0.0; bestFeature = -1
	for i in range(numFeatures):
		featList = [example[i] for example in dataSet]
		uniqueValues = set(featList)
		newGini = 0.0
		for value in uniqueValues:
			subDataSet = splitDataSet(dataSet, i, value)
			prob = len(subDataSet) / float(len(dataSet))
			newGini += prob * Gini(subDataSet)
		giniGain = baseGini - newGini
		if (giniGain > bestGiniGain):
			bestGiniGain = giniGain
			bestFeature = i
	return bestFeature



def majorityCnt(classList):
	"""
	叶节点多数表决策略
	"""
	classCount = {}
	for vote in classList:
		classCount[vote] = classCount.get(vote,0) + 1
	sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
	return sortedClassCount[0][0]

def createTree(dataSet, labels):
	"""
	创建树
	"""
	classList = [example[-1] for example in dataSet]
	if classList.count(classList[0]) == len(classList): # 类别完全相同，停止划分
		return classList[0]
	if len(dataSet[0]) == 1: # 遍历完所有特征
		return majorityCnt(classList)
	bestFeat = chooseBestFeatureToSplitByGini(dataSet)
	bestFeatLabel = labels[bestFeat]
	myTree = {bestFeatLabel:{}}
	del (labels[bestFeat])
	featValues = [example[bestFeat] for example in dataSet]
	uniqueValues = set(featValues)
	for value in uniqueValues:
		subLabels = labels[:]
		myTree[bestFeatLabel][value] = \
		createTree(splitDataSet(dataSet, bestFeat, value), subLabels)
	return myTree


#---------------------------------------------
# 使用决策树进行分类
def classify(inputTree, featLabels, testVect):
	firstStr = inputTree.keys()[0]
	secondDict = inputTree[firstStr]
	featIndex = featLabels.index(firstStr)
	for key in secondDict.keys():
		if testVect[featIndex] == key:
			if type(secondDict[key]).__name__ == 'dict':
				classLabel = classify(secondDict[key], featLabels, testVect)
			else:
				classLabel = secondDict[key]
	return classLabel



#---------------------------------------------
#使用 pickle 模块存储决策树
def storeTree(inputTree, filename):
	with open(filename, 'w') as fw:
		pickle.dump(inputTree, fw)

def loadTree(filename):
	with open(filename) as fr:
		return pickle.load(fr)



# -------------------------------------------
# 使用决策树实现
def decisionTreeBySklearn(dataSet):
	clf = DecisionTreeClassifier(random_state=0)
	clf.fit(dataSet[:,:2], dataSet[:,-1])
	print clf.predict([0.1,1.1])
	print clf.score(dataSet[:,:2], dataSet[:,-1])
	print clf.predict_proba([[0.1,1.1],[1.1,1.2]])

