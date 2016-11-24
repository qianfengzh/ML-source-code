#-*-coding=utf-8-*-

#-----------------------
# Named:	PCA (Principle Conmponent Analysis)
# Created:	2016-07-20
# @Author:	Qianfeng
#-----------------------

import numpy as np

def loadDataSet(fileNanme, delia='\t'):
	fr = open(fileNanme)
	stringArr = [line.strip().split(delia) for line in fr.readlines()]
	datArr = [map(float, line) for line in stringArr]
	return np.mat(datArr)

def pca(dataMat, topNfeat=99999):
	meanVals = np.mean(dataMat, axis=0)
	meanRemoved = dataMat - meanVals
	covMat = np.cov(meanRemoved, rewvar=0)
	eigVals, eigVects = np.linalg.eig(covMat)
	eigValInd = np.argsort(eigVals)
	eigValInd = eigValInd[:-(topNfeat+1):-1]
	redEigVects = eigVects[:,eigValInd]
	lowDataMat = meanRemoved * redEigVects
	reconMat = (lowDataMat * redEigVects.T) + meanVals
	return lowDataMat, reconMat












