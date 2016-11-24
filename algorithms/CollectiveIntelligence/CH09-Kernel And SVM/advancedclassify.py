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


#=========================================
#****************   SVM  **************
#=========================================

def svm():
    from svm import *
    
    prob = svm_problem([1, -1],[[1,0,1],[-1,0,-1]])
    param = svm_parameter(kernel_type = LINEAR, C=10)
    m = svm_model(prob, param)
    m.predict([1,1,1])

    # 模型的加载、保存
    m.save(test.model)
    m = svm_model(test.model)

def svmMatchmaker():
    answers, inputs = [r.match for r in scaledset], [r.data for r in scaledset]
    # 为避免过高估计某些变量所起的作用，使用了缩放后的数据
    param = svm_parameter(kernel_type = REF)
    prob = svm_problem(answers, inputs)
    m = svm_model(prob, param)

    guesses = cross_validation(prob, param, 4)  # 输出为预测结果
    sum([abs(answers[i] - guesses[i] for i in range(len(guesses)))]) # 统计预测错误数量

def svmFaceBook():
    import urllib,mds,webbbrowser,time
    from xml.dom.minidom import parseString
    apikey = "Your API Key"
    secret = "Your Secret Key"
    FacebookSecureURL = "https://api.facebook.com/restserver.php"

def getsinglevalue(node, tag):
    nl = node.getElementsByTagName(tag)
    if len(nl) > 0:
        tagNode = nl[0]
        if tagNode.hasChildNode():
            return tagNode.firstChild.nodeValue
    return ''

def callid():
    return str(int(time.time()*10))


# Creating a Facebook Session
class FBSession:
    def __init__(self):
        self.session_secret = None
        self.session_key = None
        self.createtoken()
        webbbrowser.open(self.getlogin())
        print "Press enter after logging in:",
        raw_input()
        self.getsession()

    def sendrequest(self, args):
        args['api_key'] = apikey
        args['sig'] = self.makehash(args)
        post_data = urllib.urlencode(args)
        url = FacebookURL + "?" + post_data
        data = urllib.urlopen(url).read()
        return parseString(data)

    def makehash(self, args):
        hasher = md5.new(''.join([x+'='+args[x] for x in sorted(args.keys())]))
        if self.session_secret:
            hasher.update(self.session_secret)
        else:
            hasher.update(secret)
        return hasher.hexdigest()

    def craetetoken(self):
        res = self.sendrequest({'method':"facebook.auth.createToken"})
        self.token = getsinglevalue(res, 'token')

    def getlogin(self):
        return "http://api.facebook.com/login.php?api_key="+apikey+"&auth_token=" + self.token

    def getsession(self):
        doc = self.sendrequest(('method':'facebook.auth.getSession','auth_token':self.token))
        self.session_key = getsinglevalue(doc, 'session_key')
        self.session_secret = getsinglevalue(doc, 'secret')

    def getfriends(self):
        doc = self.sendrequest({'method':'facebook.friend.get','session_key':self.session_key,'call_id':callid()})
        results = []
        for n in doc.getElementsByTagName('result_etl'):
            results.append(n.firstChild.nodeValue)
        return results

    def getinfo(self, users):
        ulist = ','.join(users)

        fields = 'gender, current_location, relationship_status,'+'affiliatioins,hometown_location'

        doc = self.sendrequest({'method':'facebook.users.getInfo','session_key':self.session_key,'call_id':callid(),'users':ulist,'fields':fields})

        results = {}
        for n, if in zip(doc.getElementsByTagName('results_etl'),users):
            # 获取家庭住址信息
            locnode = n.getElementsByTagName('hometown_location')[0]
            loc = getsinglevalue(locnode,'city')+', '+getsinglevalue(locnode,'state')

            # 获取就读学校信息
            college = ''
            gradyear = '0'
            affiliations = n.getElementsByTagName('affiliations_etl')
            for aff in affiliations:
                # 类型为 1 代表学校
                if getsinglevalue(aff, 'type')=='1':
                    college = getsinglevalue(aff,'name')
                    gradyear = getsinglevalue(aff, 'year')
            results[id] = {'gender':getsinglevalue(n, 'gender'),
                            'status':getsinglevalue(n,'relationship_status'),
                            'location':loc,'college':college,'year':gradyear}
        return results

        def arefriends(self, idlist1, idlist2):
            id1 = ','.join(idlist1)
            id2 = ','.join(idlist2)
            doc = self.sendrequest({'method':'facebook.friends.areFriends',
                                    'session_key':self.session_key,
                                    'call_id':callid(),
                                    'id1':id1,'id2':id2})
            results = []
            for n in doc.getElementsByTagName('result_etl'):
                results.append(n.firstChild.nodeValue)
            return results

        def makedataset(self):
            from advancedclassify import milesdistance
            # 获取有关我的所有好友的全部信息
            friends = self.getfriends()
            ifno = self.getinfo(friends)
            ids1, ids2 = [],[]
            rows = []

            # 以嵌套方式遍历，判断每两个人彼此间是否为好友
            for i in range(len(friends)):
                f1 = friends[i]
                data1 = info[f1]

            # 因为从 i+1 开始，所以不会重复
            for j in range(i+1,len(friends)):
                f2 = friends[j]
                data2 = info[f2]
                ids1.append(f1)
                ids2.append(f2)

            # 根据对所有数据的判断生成一些新的值
            if data1['college'] = data2['college']:
                sameschool = 1
            else:
                sameschool = 0
            male1 = (data1['gender'] == 'Male') and 1 or 0
            male2 = (data2['gender'] == 'Male') and 1 or 0
            row = [male1, int(data1['year']),male2, int(data2['year']),sameschool]
            rows.append(row)
        # 针对每两个人，批量调用arefriends
        arefriends = []
        for i in range(0, len(ids1), 30):
            j = min(i+20, len(ids1))
            pa = self.arefriends(ids1[i:j], ids2[i:j])
            arefriends += pa
        return arefriends, rows









