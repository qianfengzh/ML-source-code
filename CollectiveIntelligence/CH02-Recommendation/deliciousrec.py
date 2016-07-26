#-*-coding=utf-8-*-

#-----------------------
# Named:    Delicious Recommendation
# Created:  2016-07-26
# @Author:  Qianfeng
#-----------------------

from time import time
from pydelicious import get_popular,get_userposts,get_urlposts

def initializeUserDict(tag, count=1):
    user_dict={}
    # 获取前 count 个最受欢迎的连接张贴记录
    for p1 in get_popular(tag=tag)[0:count]:
        # 查找所有张贴该连接的用户
        for p2 in get_urlposts(p1['url']):
            user = p2['user']
            user_dict[user]={}
    return user_dict

def fillItems(user_dict):
    all_items = {}
    # 查找所有用户都提交过的连接
    for user in user_dict:
        for i in range(3):
            try:
                posts = get_userposts(user)
                break
            except:
                print "Faild user "+user+", retrying"
                time.sleep(4)
        for post in posts:
            url = post['url']
            user_dict[user][url] = 1.0
            all_items[url] = 1

    # 用 0 填补缺失项
    for ratings in user_dict.values():
        for item in all_items:
            if item not in ratings.keys():
                ratings[item] = 0.0








