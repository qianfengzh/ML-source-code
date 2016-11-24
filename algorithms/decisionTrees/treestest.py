#coding=utf-8
"""
decision trees created
"""
import math
import operator


def createDataSet():
    dataSet = [[1, 1, 'yes'],
               [1, 1, 'yes'],
               [1, 0, 'no'],
               [0, 1, 'no'],
               [0, 1, 'no']]
    labels = ['no surfacing','flippers']
    #change to discrete values
    return dataSet, labels


# gain the shanno entropy
def shannoEnt(dataSet):
	numEntropies = len(dataSet)
	labelCounts = {}
	for featVec in dataSet:
		featVecLabel = featVec[-1]
		labelCounts[featVecLabel] = labelCounts.get(featVecLabel,0) + 1
	shannoEntorpies = 0.0
	for key in labelCounts:
		prob =  float(labelCounts[key])/numEntropies
		shannoEntorpies -= prob * math.log(prob,2)
	return shannoEntorpies

# split dataSet according the specifical value of the feature
def splitDataSet(dataSet, axis, value):
	retDataSet = []
	for vect  in dataSet:
		if vect[axis] == value:
			reduceFeatVect = vect[:axis]
			reduceFeatVect.extend(vect[axis+1:])
			retDataSet.append(reduceFeatVect)
	return retDataSet

# choose the best feature for split dataSet
def choosBestFeat(dataSet):
	shannoEntorpies = shannoEnt(dataSet)
	numFeatures = len(dataSet[0])-1
	infoGapMax = 0.0
	bestFeatIndex = -1
	for axis in range(numFeatures):
		featValueList = [example[axis] for example in dataSet]
		uniqueFeatValue = set(featValueList)
		subShannoEnt = 0.0
		for value in uniqueFeatValue:
			retDataSet = splitDataSet(dataSet, axis, value)
			prob = len(retDataSet)/float(len(dataSet))
			subShannoEnt += prob * shannoEnt(retDataSet)
		infoGap = shannoEntorpies - subShannoEnt
		if (infoGapMax < infoGap):
			infoGapMax = infoGap
			bestFeatIndex = axis
	return bestFeatIndex

# handle the leaf node by majority count classLabel
def leafHandle(labelList):
	labelCounts = {}
	for label in labelList:
		labelCounts[label] = labelCounts.get(label,0) + 1
	sortedLabelCounts = sorted(labelCounts.iteritems(), key = operator.itemgetter, reverse = True)
	return sortedLabelCounts[0][0]

# create the decision tree
def createTree(dataSet, Labels):
	dataLabels = [Vec[-1] for Vec in dataSet]
	if dataLabels.count(dataLabels[0]) == len(dataLabels):  ## substitued by condition that -> len(set(dataLabels))==1
		return dataLabels[0]
	if len(dataSet[0]) == 1:
		return leafHandle(dataLabels)

	bestFeatIndex = choosBestFeat(dataSet)
	bestFeature = Labels[bestFeatIndex]
	del(Labels[bestFeatIndex])
	treeStructure = {bestFeature:{}}
	uniqueFeatValue = set([Vec[bestFeatIndex] for Vec in dataSet])
	for value in uniqueFeatValue:
		subLabels = Labels[:]
		treeStructure[bestFeature][value] = createTree(splitDataSet(dataSet, bestFeatIndex, value), subLabels)
	return treeStructure




