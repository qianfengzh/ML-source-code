#-*- coding=utf-8 -*-

#-----------------------
# Named:    Optimization-drom
# Created:  2016-07-31
# @Author:  Qianfeng
#-----------------------
# 学生宿舍分配优化问题

import random
import math

# 待分配的宿舍，每个宿舍两个隔间
droms=['Zeus','Athena','Hercules','Bacchus','Pluto']

# 学生的首选和次选
prefs=[('Toby', ('Bacchus', 'Hercules')),
       ('Steve', ('Zeus', 'Pluto')),
       ('Karen', ('Athena', 'Zeus')),
       ('Sarah', ('Zeus', 'Pluto')),
       ('Dave', ('Athena', 'Bacchus')), 
       ('Jeff', ('Hercules', 'Pluto')), 
       ('Fred', ('Pluto', 'Athena')), 
       ('Suzie', ('Bacchus', 'Hercules')), 
       ('Laura', ('Bacchus', 'Hercules')), 
       ('James', ('Hercules', 'Athena'))]


# 搜索定义域 [(0,9),(0,8),(0,7),(0,6),...,(0,0)]
domain = [(0,(len(droms)*2)-i-1) for i in range(0,len(droms)*2)]

def printsolution(vec):
	slots = []
	# 为每个宿舍建两个槽
	for i in range(len(droms)):
		slots += [i,i]

	# 遍历每一个学生的安置情况
	for i  in range(len(vec)):
		x = int(vec[i])

		# 从剩余槽中选择
		drom = droms[slots[x]]
		# 输出学生机器被分配的宿舍
		print prefs[i][0],drom
		# 删除该槽
		del slots[x]


def dromcost(vec):
	cost = 0
	# 建立一个槽序列
	slots = [0,0,1,1,2,2,3,3,4,4]

	# 遍历每一个学生
	for i in range(len(vec)):
		x = int(vec[i])
		drom = droms[slots[x]]
		pref = prefs[i][1]
		# 首选成本为 0 ，次选成本为 1
		if pref[0] == drom:
			cost += 0
		elif pref[1] == drom:
			cost += 1
		else:
			cost += 3

		# 删除选中的槽
		del slots[x]
	return cost
















