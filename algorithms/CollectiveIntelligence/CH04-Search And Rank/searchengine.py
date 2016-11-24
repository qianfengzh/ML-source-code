#-*-coding=utf-8-*-

#-----------------------
# Named:    Search Engine
# Created:  2016-07-28
# @Author:  Qianfeng
#-----------------------

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import re


# 构造一个单词列表，这些单词将被忽略
ignorewords = set(['the','of','to','and','a','in','is','it'])

class Crawler:
    # 初始化 Crawler 类并传入数据库名称
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # 辅助函数，用于获取条目的 id ，并且如果条目不存在，就将其加入数据库
    def getentryid(self, table, field, value, createnew=True):
        cur = self.con.execute("select rowid from %s where %s='%s'" % (table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute("insert into %s (%s) vlaues('%s')" % (table, filed, value))
            return cur.lastrowid
        else:
            return res[0]

    # 为每个网页建立索引
    def addtoindex(self, url, soup):
        if self.isindexed(url):
            return print 'Indexing ' + url
        # 获取每个单词
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # 得到 URL 的 id
        urlid = self.getentryid('urllist', 'url', url)

        # 将每个单词与该 URL 关联
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.excute("insert into wordlocation(urlid, wordid, location)\
                values(%d, %d, %d)" % (urlid, wordid, i))


    # 从一个 HTML 网页中提取文字（不带标签）
    def gettextonly(self, soup):
        v = soup.string
        if v==None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # 根据任何非空白字符进行分词处理
    def separatewords(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']

    # 如果 url 已经建过索引，则返回 true
    def isindexed(self, url):
        u = self.con.execute("select rowid from urllist where url='%s'" % url).fetchone()
        if u!=None:
            # 检查它是否已经被检索过了
            v = self.con.execute("select * from wordlocation where urlid=%d" % u[0]).fetchone()
            if v!=None:
                return True

    # 添加一个关联两个网页的链接
    def addlinkref(self, urlFrom, urlTo, linkText):
        pass

    # 从一小组网页开始进行广度优先搜索，直至某一给定深度
    #期间为网页建立索引
    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print 'Could not open %s' % page
                    continue
                soup = BeautifulSoup(c.read())
                self.addtoindex(page,soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page, link['href'])
                        if url.find("'")!=-1:
                            continue
                        url = url.split('#')[0]  # 去掉位置部分
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)
                self.dbcommit()
            pages = newpages

    # 创建数据库
    def createindextable(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table link(fromid integer, toid, integer)')
        self.con.execute('create table linkwords(wordid, linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()
        


# ===================
# 搜索类
class Searcher:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self, q):
        # 构造查询的字符串
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        # 根据单词的 ID
        words = q.split(' ')
        tablenumber = 0

        for word in words:
            # 获取单词的 ID 
            wordrow = self.com.execute("select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow != None:
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber-1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
                tablenumber += 1
        # 根据各个组分，建立查询
        fullquery = "select %s from %s where %s" % (fieldlist, tablelist, clauselist)
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]
        return rows, wordids













