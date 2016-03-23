"""
Named:   Decision Trees
Created: 2016/03/13
Author:  Qian Feng
"""
import math
import operator

# Calculate the Shannon Entries of specific dataSet
def calcShannonEnt(dataSet):
	numEntries = len(dataSet)
	labelCounts = {}
	for featVec in dataSet:
		# choose the last column
		currentLabel = featVec[-1]
		labelCounts[currentLabel] = labelCounts.get(currentLabel,0) + 1
	shannonEnt = 0.0
	for key in labelCounts:
		prob = float(labelCounts[key]/numEntries)
		shannonEnt -= prob * math.log(prob,2)
	return shannonEnt
# Split DataSet by the specific featurn
"""
Parameter:
	dataSet: the whole dataSet that would be splited
	axis: the feature which using to split the dataSet
	value: the condition of decide to split dataSet
"""
def splitDataSet(dataSet, axis, value):
	retDataSet = []
	for featVec in dataSet:
		if featVec[axis] == value:
			reduceFeatVec = featVec[:axis]
			reduceFeatVec.extend(featVec[axis+1:])
			retDataSet.append(reduceFeatVec)
	return retDataSet
# Choose the best spliting feature by using splitDataSet function to
# traverse all feature and Calculate every shannonEnt
def chooseBestFeatureToSplit(dataSet):
	numFeatures = len(dataSet[0]) - 1
	baseEntropy = calcShannonEnt(dataSet)
	bestInfoGain = 0.0
	bestFeature = -1
	for i in range(numFeatures):
		featlist = [example[i] for example in dataSet]
		uniqueVals = set(featlist)
		newEntropy = 0.0
		for value in uniqueVals:
			subDataSet = splitDataSet(dataSet, i, value)
			# 计算子划分的信息熵
			prob = len(subDataSet)/float(len(dataSet))
			newEntropy += prob* calcShannonEnt(subDataSet)
		infoGain = baseEntropy - newEntropy
		if (infoGain > bestInfoGain):
			bestInfoGain = infoGain
			bestFeature = i
	return bestFeature

# Handle the leaf node by majority count
def majorityCnt(classList):
	classCount = {}
	for vote in classList:
		classCount[vote] = classCount.get(vote, 0) + 1
	sortedClassCount = sorted(classCount.iteritems(),
		key=operator.itemgetter(1), reverse = True)
	return sortedClassCount[0][0]

# Create the decision Tree
def creatTree(dataSet,labels):
	# the list of judging class in each node
	classList = [example[-1] for example in dataSet]
	# 1) all of vector belong to a same class,stop to split
	if classList.count(classList[0]) == len(classList):
		return classList[0]
	# 2) traverse all featurn and return the majority count class
	# 因为 ID3算法 每次选取一个特征分类后，数据集都会将此特征剔除，故遍历完所有特征就只剩Label列了
	if len(dataSet[0]) == 1:
		return majorityCnt(classList)

	bestFeat = chooseBestFeatureToSplit(dataSet)
	bestFeatLabel = labels[bestFeat]
	myTree = {bestFeatLabel:{}}
	del{labels[bestFeat]}
	featValues = [example[bestFeat] for example in dataSet]
	uniqueVals = set(featValues)
	for value in uniqueVals:
		subLabels = labels[:]
		myTree[bestFeatLabel][value] = creatTree(splitDataSet\
			(dataSet,bestFeat,value),subLabels)
	return myTree