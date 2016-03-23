"""
Named:   Decision Trees Plotter
Created: 2016/03/14
Author:  Qian Feng
Func:    Plot a graph for the specific decision tree
"""

import matplotlib.pyplot as plt

# define the textbox for node
decisionNode = dict(boxstyle='sawtooth',fc='0.8')
leafNode = dict(arrowstyle='<-')

# plot the annotations which have arrows
def plotNode(nodeTxt, centerPt, parentPt, nodeType):
	createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords = 'axes fraction', xytext = centerPt, textcoords = 'axes fraction', va = 'center', ha = 'center', bbox = nodeType,arrowprops = arrw_args)
def createPlot():
	fig = plt.figure(1,facecolor='white')
	fig.clf()
	createPlot.ax1 = plt.subplot(111,frameon=False)
	plotNode('a decision node', (0.5, 0.1), (0.1, 0.5), decisionNode)
	plotNOde('a leaf node', (0.8, 0.1), (0.3, 0.8), leafNode)
	plt.show()

# Get the number of node and the number of tree's level
def getNumLeafs(treeDict):
	numLeafs = 0
	firstStr = treeDict.keys()[0]
	secondDict = treeDict[firstStr]
	for key in secondDict.keys():
		if type(secondDict[key]).__name__ == 'dict':
			numLeafs += getNumLeafs(secondDict[key])
		else:
			numLeafs += 1
	return numLeafs

def getTreeDepth(treeDict):
	maxDepth = 0
	firstStr = treeDict.keys()[0]
	secondDict = treeDict[firstStr]
	for key in secondDict.keys():
		if type(secondDict[key]).__name__ == 'dict':
			thisDepth = 1 + getTreeDepth(secondDict[key])
		else:
			thisDepth = 1
		if thisDepth > maxDepth: maxDepth = thisDepth
	return maxDepth

def retrieveTree(i):
	listOfTrees = [{'no surfacing':{0:'no',1:{'flippers':{0:'no',1:'yes'}}}},
	{'no surfacing':{0:'no',1:{'flippers':{0:{'head':{0:'no',1:'yes'}},1:'no'}}}}]
	return listOfTrees[i]