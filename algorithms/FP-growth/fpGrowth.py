#-*-coding=utf-8-*-

#-----------------------
# Named:    FP-growth
# Created:  2016-07-19
# @Author:  Qianfeng
#-----------------------

import numpy as np

class treeNode:
    '''
    构建存储树的容器类
    '''
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print ' '*ind, self.name, ' ', self.count
        for child in self.children.values():
            child.disp(ind+1)


def craeteTree(dataSet, minSup=1): 
    # minSup:支持度阈值
    # dataSet: -> dict
    '''
    Create FP Tree.
    '''
    headerTable = {}
    # 遍历第一次数据集
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) += 1

    for k in headerTable.keys():
        if headerTable[k] < minSup:
            del(headerTable[k])
    freqItemSet = set(headerTable.keys())

    if len(freqItemSet) == 0: # 判断单项频繁项集
        return None, None

    # 存放头指针和单项链接
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]
        # headerTable: {item:[count,None],item:[count,treeNode]}

    retTree = treeNode('Null Set', 1, None) # (name, count, parent)

    # 二次扫描数据集
    for tranSet, count in dataSet.items():
        localD = {} # {item:count}
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0] # gain the item count
        if len(localD) > 0: # 含有单项频繁项集
            orderedItems = [v[0] for v in sorted(localD.items(),
                key=lambda p: p[1], reverse=True)] # 按单项集频率排序
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable


def updateTree(items, inTree, headerTable, count):
    # items: list [item,item] desc by count
    if items[0] in inTree.children: # 子树中有单项时，直接计数
        inTree.children[items[0]].inc(count)
    else: # 子树中无单项时，添加子树对象节点
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 更新头指针，链接到新节点
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[itemd[0]][1], inTree.children[items[0]])

    # 拆成两部分写，是为了能写成迭代
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode




































