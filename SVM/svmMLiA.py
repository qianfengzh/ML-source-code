#coding=utf-8
"""
Named:   SVM
Created: 2016/03/25
@Author: Qian Feng
"""

import numpy as np

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
	alphas = np.mat(zeros((m, 1)))   # alphas 是一个列向量
	iterNum = 0       # 没有任何 alpha 改变的情况下遍历数据集的次数
	while (iterNum < maxIter):
		alphaPairsChanged = 0  # 记录 alpha 是否已经优化
		for i in range(m):  # 按数据集的顺序往下循环 (用全部数据集去训练)
			fXi = float(np.multiply(alphas, labelMat).T * (dataMatrix * dataMatrix[i,:].T)) + b
			Ei = fXi - float(labelMat[i])
			# 此处 if 的 condition 指的是此点分类错误，且alpha可被调整。恰好同含松弛变量的约束条件相反。
			if ((labelMat[i] * Ei < -toler) and (alpha[i] < C)) or ((labelMat[i]) * Ei > toler) and (alphas[i] > 0)):   # alpha 的取值不满足 KKT 条件，可以更改，则进入优化过程 （0<alpha<C是为了保证点不在边界上）
				j = selectJrand(i, m)    # 随机选择一个与 i 不同的向量 (即随机选出的第二个 alpha)
				fXj = float(np.multiply(alphas, labelMat).T * (dataMatrix * dataMatrix[j,:].T)) + b
				Ej = fXj - float(labelMat[j])

				alphaIold = alphas[i].copy()
				alphaJold = alphas[j].copy()
				if (labelMat[i]) != labelMat[i]:  # 保证 alpha 在 0 到 C 之间
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

				alphas[i] += labelMat[j] + labelMat[i] * (alphaJold - alphas[j])   # 对 alpha[i] 进行修改，修改量与 alpha[j]相同，但方向相反（即同时修改两个参数进行优化）
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

