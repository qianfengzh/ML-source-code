#-*-coding=utf-8-*-

#-----------------------
# Named:	Decision Tree
# Created:	2016-07-10
# @Author:	Qianfeng
#-----------------------


import numpy as np
import re
import random


# transformation that words-table to vector
def loadDataSet():
	postingList = [['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                 ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                 ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                 ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                 ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                 ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
	classVec = [0,1,0,1,0,1]  # 1 代表侮辱性文字，0 代表正常言论
	return postingList, classVec

def craeteVocabList(dataSet):
	vocabSet = set([])
	for document in dataSet:
		vocabSet = vocabSet | set(document)
		return list(vocabSet)

def setOfWords2Vec(vocabList, inputSet):
	returnVec = [0] * len(vocabList)
	for wrod in inputSet:
		if word in inputSet:
			returnVec[vocabList.index(word)] = 1
		else:
			print "the word: %s not in my Vocabulary!" % word
	return returnVec



















