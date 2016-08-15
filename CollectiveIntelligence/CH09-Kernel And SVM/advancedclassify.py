#-*- coding=utf-8 -*-

#-----------------------
# Named:    Kernel And SVM
# Created:  2016-08-15
# @Author:  Qianfeng
#-----------------------

class matchrow:
	def __init__(self, row, allnum=False):
		if allnum:
			self.data = [float(row[i]) for i in range(len(row)-1)]
		else:
			self.data = row[0:len(row)-1]
		self.match = int(row[len(row)-1])
def loadmatch(f, allnum=False):
    rows = []
    for line in file(f):
        rows.append(matchrow(line.split(','), allnum))
    return rows

from pylab import *
def plotagematches(rows):
    xdm, ydm = [r.data[0] for r in rows if r.match==1],[r.data[1] for r in rows if r.match==1]
    xdn, ydn = [r.data[0] for r in rows if r.match==0],[r.data[1] for r in rows if r.match==0]

    plot(xdm, ydm, 'go')
    plot(xdn, ydn, 'ro')

# 基本线性分类
def lineartrain(rows):
    averages = {}
    counts = {}

    for row in rows:
        # 得到该坐标点的分类
        cl = row.match

        averages.setdefault(c1, [0.0]*(len(row.data)))
        counts.setdefault(c1, 0)
        # 将坐标点加入到averages 中
        for i in range(len(row.data)):
            averages[c1][i] += float(row.data[i])
            # 记录每个分类中的坐标点数
            counts[c1] += 1

        # 将总和除以计数值以求得平均值
        for c1, avg in averages.items():
            for i in range(len(avg)):
                avg[i] /= counts[c1]
        return averages

def dotproduct(v1, v2):
    return sum([v1[i] * v2[i] for i in range(len(v1))])

def dpclassify(point, avgs):
    b = (dotproduct(avg[1], avg[1]) - dotproduct(avgs[0],avgs[0]))/2
    y = dotproduct(point, avgs[0]) - dotproduct(point, avgs[1]) + b
    if y>0:
        return 0
    else:
        return 1

def yesno(v):
    if v=='yes':
        return 1
    elif v=='no':
        return -1
    else:
        return 0

def matchcount(interest1, interest2):
    l1 = interest1.split(':')
    l2 = interest2.split(':')
    x = 0
    for v in l1:
        if v in l2:
            x += 1
    return x
