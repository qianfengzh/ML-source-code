#-*- coding=utf-8 -*-

#-----------------------
# Named:    Document Filtering
# Created:  2016-08-01
# @Author:  Qianfeng
#-----------------------

import re
import math

# 测试样例
def sampletrain(c1):
    # c1 -- Classifier instance
    c1.train('Nobody owns the water.','good')
    c1.train('the quick rabbit jumps fences','good')
    c1.train('buy pharmaceuticals now','bad')
    c1.train('make quick money at the online casino','bad')
    c1.train('the quick brown fox jumps','good')




def getWords(doc):
    spliter = re.compile('\W*')
    # 据非字母字符进行单词拆分
    words = [s.lower() for s in spliter.split(doc) if len(s)>2 and len(s)<20]

    # 只返回一组不重复的值
    return dict([(w,1) for w in words])


class Classifier:
    def __init__(self, getFeatures, filename=None):
        # 统计特征/分类组合的数量
        self.fc = {}
        # 统计每个分类中的文档数量
        self.cc = {}
        self.getFeatures = getFeatures

    def incf(self, f, cat):
        # 增加对特征/分类组合的计数值(每个特征在每个分类中出现的计数值)
        self.fc.setdefault(f,{})
        self.fc[f][cat] = self.fc[f].get(cat,0) + 1

    def incc(self, cat):
        # 增加对某一分类的计数值
        self.cc[cat] = self.cc.get(cat, 0) + 1

    def fcount(self, f, cat):
        # 某一特征出现于某一分类中的次数
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    def catcount(self, cat):
        # 属于某一分类的内容项数量
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    def totalcount(self):
        # 所有内容项的数量
        return sum(self.cc.values())

    def categories(self):
        # 所有分类的列表
        return self.cc.keys()

    def train(self, item, cat):
        features = self.getFeatures(item)
        # 针对该分类为每个特征增加计数值
        for f in features:
            self.incf(f, cat)
        # 增加该分类的计数
        self.incc(cat)

    def fprob(self, f, cat):
        if self.catcount(cat) == 0:
            return 0
        # 特征在分类中出现的总次数，除以分类中包含内容项的总数
        # 即（特征对于分类的后验概率）
        return self.fcount(f, cat) / self.catcount(cat)


    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # 计算当前的概率值
        basicprob = prf(f, cat)
    
        # 统计特征在所有分类中出现的次数
        totals = sum(self.fcount(f, c) for c in self.categories())
    
        # 计算加权平均
        bp = ((weight*ap) + (totals*basicprob)) / (weight+totals)
        return bp

class NaiveBayes(Classifier):
    def __init__(self, getFeatures):
        Classifier.__init__(self, getFeatures)
        self.thresholds = {}

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        return self.thresholds.get(cat, 1.0)

    def docprob(self, item, cat):
        features = self.getFeatures(item)

        # 将所有特征的概率相乘
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        catprob = self.catcount(cat) / self.totalcount()
        docprob = self.docprob(item, cat)
        return docprob*catprob

    def classify(self, item, default=None):
        probs = {}
        # 寻找概率最大的分类
        maxProb = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > maxProb:
                maxProb = probs[cat]
                best = cat

        # 确保概率值超过阈值 * 次大概率值
        for cat in probs:
            if cat == best:
                continue
            if probs[cat]*self.getthreshold(best)>probs[best]:
                return default
            return best


class FisherClassifier(Classifier):
    def __init__(self, getFeatures):
        Classifier.__init__(self, getFeatures)
        self.minimums = {}

    def cprob(self, f, cat):
        # 特征在该分类中出现的频率(特征对类的后验概率)
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0

        # 特征在所有分类中出现的频率
        freqsum = sum([self.fprob(f, c) for c in self.categories()])

        # 概率等于特征在该分类中出现的频率除以总体频率
        p = clf/(freqsum)
        return p

    def fisherprob(self, item, cat):
        # 将所有概率值相乘
        p = 1
        features = self.getFeatures(item)
        for f in features:
            p *= (self.weightedprob(f, cat, self.cprob))

        # 取自然对数，并乘以-2
        fscore = -2*math.log(p)

        # 利用倒置对数卡方函数求得概率
        return self.invchi2(fscore, len(features)*2)

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df//2):
            term *= m/i
            sum += term
        return min(sum, 1.0)

    def setminimum(self, cat, min):
        self.minimums[cat] = min

    def getminimum(self, cat):
        if cat not in self.minimums:
            return 0
        return self.minimums[cat]

    def classify(self, item, default=None):
        # 循环遍历并寻找最佳结果
        best = default
        maxProb = 0.0
        for c in self.categories():
            p = self.fisherprob(item, c)
            # 确保其超过下限值
            if p>self.getminimum(c) and p>maxProb:
                best = c
                maxProb = p
        return best

