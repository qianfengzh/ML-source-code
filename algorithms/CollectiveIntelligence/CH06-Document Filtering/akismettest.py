#-*- coding=utf-8 -*-

#-----------------------
# Named:    Document Filtering(Akismet API)
# Created:  2016-08-02
# @Author:  Qianfeng
#-----------------------

import akismet
defaultkey = 'YOURKEYHERE'
pageurl = "http://yoururlhere.com"
defaultagent = "Mozilla/5.0"
defaultagent += "Gecko/20060909 Firefox/1.5.0.7"

def isspam(comment, author, ipaddress, agent=defaultagent, apikey=defaultkey):
    try:
        valid = akismet.verify_key(apikey, pageurl)
        if valid:
            return akismet.comment_check(apikey, pageurl, ipaddress,agent,
                comment_content=comment, comment_author_email=author,
                comment_type='comment')
        else:
            print 'Invalid key'
            return False
    except akismet.AkismetError, e:
        print e.response, e.ststuscode
        return False









