#-*-coding=utf-8-*-

#-----------------------
# Named:	Decision Trees Plotter
# Created:	2016-07-10
# @Author:	Qianfeng
#-----------------------

import matplotlib.pyplot as plt 

decisionNode = dict(boxstyle='sawtooth', fc='0.8')
leafNode = dict(boxstyle='round4', fc='0.8')
arrow_args = dict(arrowstyle='<-')

def plotNode(nodeTxt, centerPt, parentPt, nodeType):
	createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction', \
		xytext=centerPt, textcoords='axes fraction', va='center', ha='center', \
		bbox=nodeType, arrowprops=arrow_args)

def createPlot():
	fig = plt.figure(1, facecolor='white')
	fig.clf()
	createPlot.ax1 = plt.subplot(111, frameon=False)
	plotNode(U'决策节点', (0.5, 0.1), (0.1, 0.5), decisionNode)
	plotNode(U'叶节点', (0.8, 0.1), (0.3, 0.8), leafNode)
	plt.show()

#-------------------------------------------------------------------
# 构造注解树

# 双递归，探测树深度
def getNumLeafs(myTree):
	"""
	递归获取叶节点总数
	"""
	numLeafs = 0
	firstStr = myTree.keys()[0]
	secondDict = myTree[firstStr]
	for key in secondDict.keys():
		if type(secondDict[key]).__name__ == 'dict':
			numLeafs += getNumLeafs(secondDict[key])
		else:
			numLeafs += 1
	return numLeafs

def getTreeDepth(myTree):
	"""
	递归获取树深度
	"""
	maxDepth = 0
	firstStr = myTree.keys()[0]
	secondDict = myTree[firstStr]
	for key in secondDict.keys():
		if type(secondDict[key]).__name__ == 'dict':
			thisDepth = 1+ getTreeDepth(secondDict[key])
		else:
			thisDepth = 1
		if thisDepth > maxDepth:
			maxDepth = thisDepth
	return maxDepth

def retrieveTree(i):
	listOfTrees = [{'no surfacing': {0: 'no', 1: {'flippers': {0: 'no', 1: 'yes'}}}},\
                  {'no surfacing': {0: 'no', 1: {'flippers': {0: {'head': {0: 'no', 1: 'yes'}}, 1: 'no'}}}}
                  ]
	return listOfTrees[i]    






