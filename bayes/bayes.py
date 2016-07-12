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

def createVocabList(dataSet):
	vocabSet = set([])
	for document in dataSet:
		vocabSet = vocabSet | set(document)
	return list(vocabSet)

def setOfWords2Vec(vocabList, inputSet):
	returnVec = [0] * len(vocabList)
	for word in inputSet:
		if word in inputSet:
			returnVec[vocabList.index(word)] = 1
		else:
			print "the word: %s not in my Vocabulary!" % word
	return returnVec

def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    # 先验概率
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    p0Num = np.zeros(numWords)
    p1Num = np.zeros(numWords)
    p0Dencom = 0.0
    p1Dencom = 0.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Dencom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Dencom += sum(trainMatrix[i])
    p1Vect = np.log((p1Num+1) / (p1Dencom+2))
    p0Vect = np.log((p0Num+1) / (p0Dencom+2))
    return p0Vect, p1Vect, pAbusive


def classifyNB(vec2Classify, p0Vect, p1Vect, pClass1): # 求取过 log 函数，故公式中的累乘在此处直接用累加表示
    p1 = sum(vec2Classify * p1Vect) + np.log(pClass1) # 特征的后验概率与词集向量相乘，是去相应词集的后验概率
    p0 = sum(vec2Classify * p0Vect) + np.log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else:
        return 0

def testingNB():
    listOPosts, listClasses = loadDataSet()
    myVocabList = createVocabList(listOPosts)
    trainMat = []
    for postingDoc in listOPosts:
        trainMat.append(setOfWords2Vec(myVocabList, postingDoc))
    p0V, p1V, pAb = trainNB0(np.array(trainMat), np.array(listClasses))
    testEntry = ['love', 'my', 'dalmation']
    thisDoc = np.array(setOfWords2Vec(myVocabList, testEntry))
    print testEntry,'classified as: ',classifyNB(thisDoc, p0V, p1V, pAb)
    testEntry = ['stupid', 'garbage']
    thisDoc = np.array(setOfWords2Vec(myVocabList, testEntry))
    print testEntry,'classified as: ',classifyNB(thisDoc, p0V, p1V, pAb)
    

def bagOfWords2VecMN(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in inputSet:
            returnVec[vocabList.index(word)] += 1
        else:
            print "the word: %s not in my Vocabulary!" % word
    return returnVec


def textParse(bigString):
    listOfTokens = re.split(r'\W*',bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]

def spamTest():
    docList=[]
    classList = []
    fullText = []
    for i in range(1,26):
        wordList = textParse(open('D:\\tmp\\email\\spam\\%d.txt' % i).read())
        docList.append(wordList) # 一条邮件作为一个列表元素
        fullText.extend(wordList)
        classList.append(1) # '1'表示垃圾邮件
        wordList = textParse(open('D:\\tmp\\email\\ham\\%d.txt' % i).read())
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList = createVocabList(docList)
    trainingSet = range(50)
    testSet = []
    for i in range(10):
        randIndex = int(random.uniform(0,len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del (trainingSet[randIndex])
    trainMat = []
    trainClasses = []
    for docIndex in trainingSet:
        trainMat.append(setOfWords2Vec(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V, p1V, pSpam = trainNB0(np.array(trainMat),np.array(trainClasses))
    errorCount = 0
    for docIndex in testSet:
        wordVector =  setOfWords2Vec(vocabList, docList[docIndex])
        if classifyNB(np.array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
            errorCount += 1
    print 'the error rate is: ',float(errorCount) / len(testSet)












