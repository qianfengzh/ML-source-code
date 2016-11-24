'''
树回归与标准回归的比较
'''
# 树回归预测
def  regTreeEval(model, inDat):
	return float(model)

def modelTreeEval(model, inDat):
	n = np.shape(inDat)[1]
	X = np.mat(np.ones((1,n+1)))
	X[:,1:n+1] = inDat
	return float(X * model)

def treeForeCast(tree, inData, modelEval=regTreeEval):
	if not isTree(tree):
		return modelEval(tree, inData)

	if inData[tree['spInd']] > tree['spVal']:
		if isTree(tree['left']):
			return treeForeCast(tree['left'], inData, modelEval)
		else:
			return modelEval(tree['left'], inData)
	else:
		if isTree(tree['right']):
			return treeForeCast(tree['right'], inData, modelEval)
		else:
			return modelEval(tree['right'], inData)

def createForeCast(tree, testData, modelEval=regTreeEval):
	m = len(testData)
	yHat = np.mat(np.zeros((m,1)))
	for i in range(m):
		yHat[i,0] = treeForeCast(tree, np.mat(testData[i]), modelEval)
	return yHat

"""
1、分别生成标准回归模型、树回归模型、模型回归模型；
2、利用生成的模型，分别对测试集进行预测；
3、分别求出三个模型的预测值与正确分类标签的相关系数；
4、比较三个模型的相关系数。
"""