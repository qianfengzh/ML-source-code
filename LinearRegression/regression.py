#-*-coding=utf-8-*-

#-----------------------
# Named:	Linear Regression
# Created:	2016-07-15
# @Author:	Qianfeng
#-----------------------

import numpy as np

def loadDataSet(fileName):
	numFeat = len(open(fileName).readline().split('\t')) - 1
	datMat = []
	labelMat = []
	fr = open(fileName)
	for line in fr.readlines():
		lineArr = []
		curLine = line.strip().split('\t')
		for i in range(numFeat):
			lineArr.append(float(curLine[i]))
		datMat.append(lineArr)
		labelMat.append(float(curLine[-1]))
	return datMat, labelMat

def standRegres(xArr, yArr):
	xMat = np.mat(xArr)
	yMat = np.mat(yArr).T
	xTx = xMat.T * xMat
	if np.linalg.det(xTx) == 0.0: # 计算 xTx 矩阵的行列式，判定是否可逆
		print 'This matrix is singular, cannot do inverse'
		return
	ws = xTx.I * (xMat.T * yMat)
	return ws
	

