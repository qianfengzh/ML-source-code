#coding=utf-8
"""
Named:   SVM
Created: 2016/03/25
@Author: Qian Feng
"""

import numpy as np
import random

def loadDataSet(filename):
	dataMat = []
	labelMat = []
	with open(filename) as fr:
		for line in fr.readlines():
			lineArr = line.strip().split('\t')
			dataMat.append([float(lineArr[0]), float(lineArr[1])])
			labelMat.append(float(lineArr[2]))
	return dataMat,labelMat

def selectJrand(i, m):
	j = i
	while (j == i):
		j = int(random.uniform(0,m))
	return j

def clipAlpha(aj, H, L):
	if aj > H:
		aj = H
	if L > aj:
		aj = L
	return aj



# Simple SMO algorithm
def smoSimple(dataMatIn, classLabels, C, toler, maxIter):   # C 是惩罚系数，toler 是松弛变量
	dataMatrix = np.mat(dataMatIn)
	labelMat = np.mat(classLabels).transpose()   # labelMat 是一个列向量
	b = 0

	m, n = np.shape(dataMatrix)
	alphas = np.mat(np.zeros((m, 1)))   # alphas 是一个列向量
	iterNum = 0       # 没有任何 alpha 改变的情况下遍历数据集的次数
	while (iterNum < maxIter):

		alphaPairsChanged = 0  # 记录 alpha 是否已经优化
		for i in range(m):  # 按数据集的顺序往下循环 (用全部数据集去训练)
			fXi = float(np.multiply(alphas, labelMat).T * (dataMatrix * dataMatrix[i,:].T)) + b
			Ei = fXi - float(labelMat[i]) #if checks if an example violates KKT conditions
			# 此处 if 的 condition 指的是此点分类错误，且alpha可被调整。恰好同含松弛变量的约束条件相反。
			# alpha 的取值不满足 KKT 条件，可以更改，则进入优化过程 （0<alpha<C是为了保证点在边界上，即此点可以作为支持向量）
			if ((labelMat[i] * Ei < -toler) and (alphas[i] < C)) or ((labelMat[i] * Ei > toler) and (alphas[i] > 0)):
				j = selectJrand(i, m)    # 随机选择一个与 i 不同的向量 (即随机选出的第二个 alpha)
				fXj = float(np.multiply(alphas, labelMat).T * (dataMatrix * dataMatrix[j,:].T)) + b
				Ej = fXj - float(labelMat[j])

				alphaIold = alphas[i].copy()
				alphaJold = alphas[j].copy()
				if (labelMat[i] != labelMat[j]):
					L = max(0, alphas[j] - alphas[i])
					H = min(C, C + alphas[j] - alphas[i])
				else:               
					L = max(0, alphas[j] + alphas[i] - C)
					H = min(C, alphas[j] + alphas[i])
				#########################################
				if L == H:
					print "L==H"
					continue

				eta = 2.0 * dataMatrix[i,:] * dataMatrix[j,:].T - dataMatrix[i,:] * dataMatrix[i,:].T - dataMatrix[j,:] * dataMatrix[j,:].T   # eta = -2*(Xi-Xj)^2   eta 是 alpha[j]的最佳修改量
				if eta >= 0:   # 因为通常情况下目标函数是正定的，也就是说，能够在直线约束方向上求得最小值，并且eta > 0
					print "eta >= 0"
					continue

				alphas[j] -= labelMat[j] * (Ei - Ej)/eta
				alphas[j] = clipAlpha(alphas[j], H, L)
				if (abs(alphas[j] - alphaJold) < 0.00001):
					print "j not moving enough"
					continue

				alphas[i] += labelMat[j] * labelMat[i] * (alphaJold - alphas[j])   # 对 alpha[i] 进行修改，修改量与 alpha[j]相同，但方向相反（即同时修改两个参数进行优化）
				# 是为了满足将除 alpha[i] 和 alpha[j] 之外的 alpha 作为定值的假设
				b1 = b - Ei - labelMat[i] * (alphas[i] - alphaIold) * dataMatrix[i,:] * dataMatrix[i,:].T - labelMat[j] * (alphas[j] - alphaJold) * dataMatrix[i,:] * dataMatrix[j,:].T
				b2 = b - Ej - labelMat[i] * (alphas[i] - alphaIold) * dataMatrix[i,:] * dataMatrix[j,:].T - labelMat[j] * (alphas[j] - alphaJold) * dataMatrix[j,:] * dataMatrix[j,:].T
				if (0 < alphas[i]) and (C > alphas[i]):
					b = b1
				elif (0 < alphas[j]) and (C > alphas[j]):
					b = b2
				else:
					b = (b1 + b2)/2.0
				alphaPairsChanged += 1
				print "iterNum: %d i:%d, pairs changed %d" % (iterNum, i, alphaPairsChanged)
		if (alphaPairsChanged == 0):
			iterNum += 1
		else:
			iterNum = 0
		print "iteration number: %d" % iterNum
	return b, alphas




class optStruct:
	def __init__(self,dataMatIn, classLabels, C, toler)
	self.X = dataMatIn
	self.labelMat = classLabels
	self.C = C
	self.tol = toler
	self.m = np.shape(dataMatIn)[0]
	self.alphas = np.mat(np.zeros((self.m, 1)))
	self.b = 0
	self.eCache = np.mat(zeros((self.m, 2))) # 误差缓存,第一列是是否有效的标志位，第二列是给出的实际E值

def calcEk(oS, k):
	fXk = float(np.multiply(oS.alphas, oS.labelMat).T * (oS.X * oS.X[k,:].T)) + oS.b
	Ek = fXk - float(oS.labelMat[k])
	return Ek

def selectJ(i, oS, Ei):  # 内循环中启发式搜索
	maxK = -1; maxDeltB = 0; Ej = 0
	oS.eCache[i] = [1,Ei]
	validEcacheList = np.nonzero(oS.eCache[:,0].A)[0] # 将有效值的行坐标返回
	if (len(validEcacheList)) > 1:
		for k in validEcacheList:
			if k == i:
				continue
			Ek = calcEk(oS, k)
			deltaE = abs(Ei - Ek)
			if (deltaE > maxDeltB):  # 选择具有最大步长的j
				maxK = k
				maxDeltaE = deltaE
				Ej = Ek
		return maxK, Ej
	else:
		j = selectJrand(i, oS.m)
		Ej = calcEk(oS, j)
	return j, Ej

def updateEk(oS, k):
	Ek = calcEk(oS, k)
	oS.eCache[k] = [1, Ek]