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

# 采用共同兴趣列表能更好的去衡量两者之间的相似度
# 更进一步的细分共同兴趣列表方式
#（通过对兴趣进行划分层级，如大、小类，在同一项目中相似度权重更高，在同一大类中相似度稍小）
def matchcount(interest1, interest2):
    l1 = interest1.split(':')
    l2 = interest2.split(':')
    x = 0
    for v in l1:
        if v in l2:
            x += 1
    return x


# Yahoo API 使用，利用API返回的经纬度信息，计算两地之间的距离
def milesdistance(a1, a2):
    return 0

def getlocation(address):
    yahookey = "Your Key Here"
    from xml.dom.minidom import parseString
    from urllib import urlopen, quote_plus

    loc_cache = {}

    if address in loc_cache:
        return loc_cache[address]
    data = urlopen('http://api.local.yahoo.com/MapsService/V1/'+'geocode?appid=%s&location=%s' %
        (yahookey, quote_plus(address))).read
    doc = parseString(data)
    lat = doc.getElementsByTagName('Latitude')[0].firstChild.nodeValue
    long = loc.getElementsByTagName('Longitude')[0].firstChild.nodeValue
    loc_cache[address] = (float(lat), float(long))
    return loc_cache[address]

# 使用 euclid 距离，区别在于，将维度间的差值乘以69.1，经度之间的差值乘以53
def milesdistance(a1, a2):
    lat1, long1 = getlocation(a1)
    lat2, long2 = getlocation(a2)
    latdif = 69.1 * (lat2-lat1)
    longdif = 53.0 * (long2-long1)
    return (latdif**2 + long1**2)**.5

# 构造数据集
def loadnumerical():
    oldrows = loadmatch('matchmaker.csv')
    newrows = []
    for row in oldrows:
        d = row.data
        data = [float(d[0]), yesno(d[1]), yesno(d[2]),
            float(d[5]), yesno(d[6]), yesno(d[7]), 
            matchcount(d[3], d[8]),
            milesdistance(d[4], d[9]),
            row.match]

def scaledata(rows):
    low = [999999999.0] * len(rows[0].data)
    high = [-999999999.0] * len(rows[0].data)
    # 寻找最大值和最小值
    for row in rows:
        d = row.data
        for i in range(len(d)):
            if d[i] < low[i]: low[i] = d[i]
            if d[i] > high[i]: high[i] = d[i]

    # 对数据进行缩放处理的函数
    def scaleinput(d):
        return [(d.data[i] - low[i])/(high[i] - low[i])
            for i in range(len(low))]
    
    # Scale all the data
    # 对所有数据进行缩放处理
    newrows = [matchrow(scaleinput(row.data)+[row.match]) for row in rows]

    # 返回新的数据和缩放处理函数
    return newrows, scaleinput


#=========================================
#****************   核函数  **************
#=========================================
# 径向基函数核（非线性）
def rbf(v1, v2, gamma=20):
    dv = [v1[i] - v2[i] for i in range(len(v1))]
    l = veclength(dv)
    return math.e**(-gamma*l)

# 先通过径向基函数对左边进行变换，再去计算各类的均值点
def nlclassify(point, rows, offset, gamma=10):
    sum0 = 0.0
    sum1 = 0.0
    count0 = 0
    count1 = 0

    for row in rows:
        if row.match == 0:
            sum0 += rbf(point, row.data, gamma)
            count0 += 1
        else:
            sum1 += rbf(point, row.data, gamma)
            count1 += 1
        y = (1.0/count0)*sum0 - (1.0/count1)*sum1 + offset

        if y<0:
            return 0
        else:
            return 1

def getoffset(rows, gamma=10):
    l0 = []
    l1 = []
    for row in rows:
         if row.match == 0:
            l0.append(row.data)
        else:
            l1.append(row.data)
    sum0 = sum(sum([rbf(v1, v2, gamma) for v1 in l0]) for v2 in l0)
    sum1 = sum(sum([rbf(v1, v2, gamma) for v1 in l1]) for v2 in l1)
    return (1.0/(len(l1)**2))*sum1 - (1.0/(len(l0)**2))*sum0




