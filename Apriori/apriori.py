#-*-coding=utf-8-*-

#-----------------------
# Named:    K-Means
# Created:  2016-07-18
# @Author:  Qianfeng
#-----------------------

import numpy as np

def loadDataSet():
    return [[1,3,4],[2,3,5],[1,2,3,5],[2,5]]

def createC1(dataSet): # 创建大小为1的所有候选项集的集合
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1: # 滤除重复项
                C1.append([item])
        C1.sort()
    return map(frozenset, C1) # 对C1中的每个项构建一个不变集合，目的是后面需要每个项集来做字典的键，以对项集进行计数

def scanD(dataSet, Ck, minSupport):
    ssCnt = {} # 支持度计数存储
    for tid in dataSet: # 支持度计数
        for can in Ck:
            if can.issubset(tid):
                ssCnt[can] = ssCnt.get(can,0) + 1            
    numItems = float(len(dataSet))
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key] / numItems # 计算所有项集的支持度
        if support >= minSupport:
            retList.insert(0,key)
        supportData[key] = support
    return retList, supportData # 返回 Lk 和各项集的支持度

def aprioriGen(Lk, k): # creates Ck(使用 Lk 来创建 Ck+1)
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk): # 前 k-2 个元素相同时，合并两个集合
            L1 = list(Lk[i])[:k-2]
            L2 = list(Lk[j])[:k-2]
            L1.sort()
            L2.sort()
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList

def apriori(dataSet, minSupport=0.5):
    C1 = createC1(dataSet)
    L1, supportData = scanD(dataSet, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0): # 判断 Lk 是否为空，以构成 Ck+1
        Ck = aprioriGen(L[k-2], k)
        Lk, supK = scanD(dataSet, Ck, minSupport) # 使用支持度阈值进行过滤
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData

# 关联规则生成函数(主函数)
def generateRules(L, supportData, minConf=0.7):
    bigRuleList = []
    for i in range(1, len(L)): # i+1项频繁项集
        for freqSet in L[i]: # i项频繁项集集合中的每个 i 项频繁集
            H1 = [frozenset([item]) for item in freqSet] # 将 i 项频繁项集拆成 i 个元素
            if (i > 1): # H1用作规则后件
                rulesFromConseq(freqSet, H1, supportData, bigRuleList, minConf)
            else:
                calcConf(freqSet, H1, supportData, bigRuleList, minConf)
    return bigRuleList

def calcConf(freqSet, H, supportData, br1, minConf=0.7): # H为规则后件
    prunedH = []
    for conseq in H:
        conf = supportData[freqSet] / supportData[freqSet-conseq] # 集合操作（差集）
        if conf >= minConf:
            br1.append((freqSet-conseq, conseq, conf)) # freqSet-conseq 为规则前件
            prunedH.append(conseq)
    return prunedH

def rulesFromConseq(freqSet, H, supportData, br1, minConf=0.7): # H为规则后件
    m = len(H[0])
    if (len(freqSet) > (m + 1)):
        Hmp1 = aprioriGen(H, m+1)
        Hmp1 = calcConf(freqSet, Hmp1,supportData, br1, minConf)
        if (len(Hmp1) > 1):
            rulesFromConseq(freqSet, Hmp1, supportData, br1, minConf)














