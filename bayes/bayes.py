#coding=utf-8
"""
Named:   Naive Bayes
Created: 2016/03/19
@Author:  Qian Feng
"""
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

def createVocabList(dataSet):
	vocabSet = set([])
	for documnet in dataSet:
		vocabSet = vocabSet | set(documnet)  # 创建两个几何的并集
	return list(vocabSet)

# set-of-words model  # 词集模型
def setOfWords2Vec(vocabList, inputSet):
	returnVec = [0]*len(vocabList)    # 创建一个其中所含元素都为0的向量
	for word in inputSet:
		if word in vocabList:
			returnVec[vocabList.index(word)] = 1
		else:
			print "the word: %s is not in my Vocabulary!" % word
	return returnVec

# bag-of-words model  # 词袋模型
def bagOfWords2VecMN(vocabList, inputSet):
	returnVec = 0 * len(vocabList)
	for word in vocabList:
		if word in vocabList:
			returnVec[vocabList.index(word)] += 1
	return returnVec


# P(c1|w) = (P(w|c1)*P(c1))/P(w)
# the trainMatrix size equals the vocabulary size,
# because the trainMatrix is the list throughing setOfWords2Vec
def trainNB0(trainMatrix, trainCategory):
	numTrainDocs = len(trainMatrix)
	numWords = len(trainMatrix[0])
	pAbusive = sum(trainCategory)/float(numTrainDocs)    # P(c1) sum(trainCategory) is the number of abusive because the trainCategory's value is 0 or 1
	# p0Num = zeros(numWords)
	# p1Num = zeros(numWords)
	# p0Denom = 0.0
	# p1Denom = 0.0
	p0Num = np.ones(numWords)
	p1Num = np.ones(numWords)
	p0Denom = 2.0
	p1Denom = 2.0
	for i in range(numTrainDocs):
		if trainCategory[i] == 1:
			p1Num += trainMatrix[i]
			p1Denom += sum(trainMatrix[i])
		else:
			p0Num += trainMatrix[i]
			p0Denom += sum(trainMatrix[i])
	# p1Vect = p1Num/p1Denom      # change to log()
	# p0Vect = p0Num/p0Denom      # change to log()
	p1Vect = np.log(p1Num/p1Denom)      
	p0Vect = np.log(p0Num/p0Denom)
	return p0Vect, p1Vect, pAbusive   # 返回的是两个类条件概率和一个类概率（因为是2分类模型，另一类概率可简单求得）


# naive bayes classify function
# 利用 bayes 公式，计算两个向量条件类概率时，分母都要除掉向量概率（P(w)），故可将其省略
# naive bayes classify function
def classifyNB(vec2Classify, p0Vec, p1Vec, pClass):
	p1 = sum(vec2Classify * p1Vec) + np.log(pClass)
	p0 = sum(vec2Classify * p0Vec) + np.log(1.0 - pClass)
	if p1 > p0:
		return 1
	else:
		return 0

# test Naive Bayes classify function
def testingNB():
	listOPosts, listClasses = loadDataSet()
	myVocabList = createVocabList(listOPosts)
	trainMat = []
	for postinDoc in listOPosts:
		trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
	p0V, p1V, pAb = trainNB0(np.array(trainMat), np.array(listClasses))

	testEntry = ['love', 'my', 'dalmation']
	thisDoc = np.array(setOfWords2Vec(myVocabList, testEntry))
	print testEntry,'classified as: ',classifyNB(thisDoc, p0V, p1V, pAb)
	
	testEntry = ['stupid', 'garbage']
	thisDoc = np.array(setOfWords2Vec(myVocabList, testEntry))
	print testEntry,'classified as: ',classifyNB(thisDoc, p0V, p1V, pAb)





"""
Testing algorithm.
Making a cross validation by navie bayes.
"""
# text parse and spam email test function
def textParse(bigString):
	# import re
	listOfTokens = re.split(r'\w*', bigString)
	return [tok.lower() for tok in listOfTokens if len(tok) > 2]

def spamTest():
	docList = []
	classList = []
	fullText = []
	for i in range(1,26):
		with open('D:\\python\\email\\spam\\%d.txt' % i) as ft:
			wordList = textParse(ft.read())
		docList.append(wordList)
		fullText.extend(wordList)
		classList.append(1)
		with open('D:\\python\\email\\ham\\%d.txt' % i) as ft:
			wordList = textParse(ft.read())
		docList.append(wordList)
		fullText.extend(wordList)
		classList.append(0)
	vocabList = createVocabList(docList)
	# build a random trainSet
	# 80% data to training and the leave 20% to testing (cross validation)
	trainingSet = range(50)
	testSet = []
	for i in range(10):
		randIndex = int(random.uniform(0,len(trainingSet)))
		testSet.append(trainingSet[randIndex])
		del(trainingSet[randIndex])
	trainMat = []
	trainClasses = []
	for docIndex in trainingSet:
		trainMat.append(setOfWords2Vec(vocabList, docList[docIndex]))
		trainClasses.append(classList[docIndex])
	p0V, p1V, pSpam = trainNB0(np.array(trainMat), np.array(trainClasses))
	errorCount = 0
	for docIndex in testSet:
		wordVector = setOfWords2Vec(vocabList, docList(docIndex))
		if classifyNB(np.array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
			errorCount += 1
	print 'the error rate is: ',float(errorCount)/len(testSet)




##############
# RSS source #
##############

# caculate the frequence
def calcMostFre(vocabList, fullText):
	import operator
	freqDict = {}
	for token in vocabList:
		freqDict[token] = fullText.count(token)
	sortedFreq = sorted(freqDict.iteritems(), key=operator.itemgetter(1), reverse=True)
	return sortedFreq[:30]

def localWords(feed1,feed0):
	import feedparser
	docList = []
	classList = []
	fullText = []
	minLen = min(len(feed1['entries']),len(feed0['entries']))
	for i in range(minLen):
		wordList = textParse(feed1['entries'][i]['summary'])
		docList.append(wordList)
		fullText.extend(wordList)
		classList.append(1)
		wordList = textParse(feed0['entries'][i]['summary'])
		docList.append(wordList)
		fullText.extend(wordList)
		classList.append(0)
	vocabList = createVocabList(docList)
	top30Words = calcMostFre(vocabList, fullText)
	for pairW in top30Words:
		if pairW[0] in vocabList:
			vocabList.remove(pairW[0])

	trainingSet = range(2*minLen)
	testSet = []
	for i in range(20):
		randIndex = int(random.uniform(0,len(trainingSet)))
		testSet.append(trainingSet[randIndex])
		del (trainSet[randIndex])
	trainMat = []
	trainClasses = []
	for docIndex in trainingSet:
		trainMat.append(bagOfWords2VecMN(vocabList, docList[docIndex]))
		trainClasses.append(classList[docIndex])
	p0V, p1V, pSpam = trainNB0(np.array(trainMat),np.array(trainClasses))
	errorCount = 0
	for docIndex in testSet:
		wordVector = bagOfWords2VecMN(vocabList, docList[docIndex])
		if classifyNB(np.array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
			errorCount += 1
	print 'the error rate is: ',float(errorCount)/len(testSet)
	return vocabList, p0V, p1V     # 返回词列表 和 两个类条件概率向量


# 最具表征性的词汇显示函数
def getTopWords(ny, sf):
	import operator
	vocabList, p0V, p1V=localWords(ny, sf)
	topNY = []
	topSF = []
	for i in range(len(p0V)):
		# -6.0 是经过 log 函数处理过的，转换过来之后，词向量中各词出现的概率必须大于 0.000001
		if p0V[i] > -6.0 : topSF.append((vocabList[i],p0V[i]))
		if p1V[i] > -6.0 : topNY.append((vocabList[i],p0V[i]))
	sortedSF = sorted(topSF, key=lambda pair:pair[1], reverse=True)
	print 'SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**'
	for item in sortedSF:
		print item[0]
	sortedNY = sorted(topNY, key=lambda pair:pair[1], reverse=True)
	print 'NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**'
	for item in sortedNY:
		print item[0]