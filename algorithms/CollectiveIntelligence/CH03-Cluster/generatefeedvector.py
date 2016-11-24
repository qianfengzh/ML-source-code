#-*-coding=utf-8-*-

#-----------------------
# Named:    Gain Info From Rss Origin
# Created:  2016-07-27
# @Author:  Qianfeng
#-----------------------

import feedparser
import re

# 返回一个RSS订阅源的标题和包含单词计数情况的字典
def getwordcounts(url):
    # 解析订阅源
    d = feedparser.parser(url)
    wc = {}

    # 循环遍历所有的文章条目
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description

        # 提取一个单词列表
        words = getwords(e.title + ' ' + summary)
        for word in words:
            wc[word] = wc.get(word,0) + 1
    return d.feed.title, wc

def getwords(html):
    # 除掉 html 标记
    txt = re.compile(r'<[^>]+>').sub(''.html)

    # 利用所有非字母字符拆分出单词
    words = re.compile(r'[^A-Z^a-z]+').split(txt)

    # 转化成小写形式
    return [word.lower() for word in words if word!='']


# 主体程序
apcount = {}
wordcounts = {}
feedlist = [line for line in file('feed.txt')]
for feedurl in feedlist:
    title, wc = getwordcounts(feedurl)
    wordcounts[title] = wc
    for word, count in wc.items():
        apcount.setdefault(word,0)
        if count > 1:
            apcount[word] += 1

# 过滤常用词
wordlist = {}
for w, bc in apcount.items():
    frac = float(bc)/len(feedlist)
    if frac > 0.1 and frac < 0.5:
        wordlist.append(w)


