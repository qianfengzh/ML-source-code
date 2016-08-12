#-*- coding=utf-8 -*-

#-----------------------
# Named:    Price Models
# Created:  2016-08-11
# @Author:  Qianfeng
#-----------------------


from random import random,randint
import math

def wineprice(rating, age):
	peak_age = rating-50

	# 根据等级来计算计算价格
	price = rating/2
	if age > peak_age:
		# 经过“峰值年”，后继5年里其品质将会变差
		price = price * (5-(age-peak_age))
	else:
		price = price * (5*((age+1)/peak_age))
		#价格在接近“峰值年”是会增加到原值的5倍
	if price < 0:
		price = 0
	return price


def wineset1():
	rows = []
	for i in range(300):
		# 随机生成年代和等级
		rating = random()*50 + 50
		age = random()*50
		
		# 得到一个参考价格
		price = wineprice(rating, age)
		
		# 增加“噪声”
		price *= (random()*0.4 + 0.8)
		
		# 加入数据集
		rows.append({'input':(rating,age),
					'result':price})
	return rows

def euclidian(v1, v2):
	d = 0.0
	for i in range(len(v1)):
		d += (v1[i]-v2[i])**2
	return math.sqrt(d)

def getdistance(data, vec1):
	distancelist = []
	for i in range(len(data)):
		vec2 = data[i]['input']
		distancelist.append((euclidian(vec1, vec2),i))
	distancelist.sort()
	return distancelist

def knnestimate(data, vec1, k=5):
	# 得到排序过后的距离列表
	dlist = getdistance(data, vec1)

	avg = 0.0
	# 对前 k 项结果求平均
	for i in range(k):
		idx = dlist[i][1]
		avg += data[idx]['result']
	return avg/k


# 使用反函数为近邻分配权重(缺点：衰减过快)
def inverseweight(dist, num=1.0, const=0.1):
	return num/(dist+const)

# 使用减法函数计算权重(解决反函数对近邻分配权重过大问题；缺点：权重会跌至0)
# 无法找到距离足够近的项
def subtraceweight(dist, const=1.0):
	if dist > const:
		return 0
	else:
		return const-dist

# 高斯函数（钟形曲线）
def gaussian(dist, sigma=1.0):
	return math.exp(-dist**2/(2*sigma**2))


def weightedknn(data, vec1, k=5, weightf=gaussian):
	# 得到距离
	dlist = getdistance(data, vec1)
	avg = 0.0
	totalweight = 0.0

	# 得到加权平均值
	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]
		weight = weightf(dist)
		avg += weight * data[idx]['result']
		totalweight += weight
	avg /= totalweight
	return avg




