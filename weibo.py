#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
文档生成用sphinx

模块:weibo
    一个微博爬虫模块。作者pythonwood。

    起因是为了看《一些事一些情》的微博评论更方便。

使用sphinx生成本文档

可释放了，但代码可压缩，以后再做 2014-03-20

微博探测笔记：
    根据用户名字找id，根据源文件html嵌入的JS代码::

        $CONFIG['oid']='1093974672'; 

    评论search，每三个一组，首页包含3次。

    (pre_page=0,page=1,pagebar=0),(pre_page=1,page=1,pagebar=0),(pre_page=1,page=1,pagebar=1)

    http://weibo.com/p/aj/mblog/mbloglist?_wv=5&domain=100505&pre_page=0&page=1&max_id=3708816657175473&end_id=3716789328888062&count=15&pagebar=0&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__24&id=1005051716235922&script_uri=/p/1005051716235922/weibo&feed_type=0&profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1&__rnd=1401772208635

    http://weibo.com/p/aj/mblog/mbloglist?_wv=5&domain=100505&pre_page=1&page=1&max_id=3708816657175473&end_id=3716789328888062&count=15&pagebar=0&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__24&id=1005051716235922&script_uri=/p/1005051716235922/weibo&feed_type=0&profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1&__rnd=1401772208635

    http://weibo.com/p/aj/mblog/mbloglist?_wv=5&domain=100505&pre_page=1&page=1&max_id=3708816657175473&end_id=3716789328888062&count=15&pagebar=1&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__24&id=1005051716235922&script_uri=/p/1005051716235922/weibo&feed_type=0&profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1&__rnd=1401772208635

    返回格式::

        {"code":"100000","msg":"","data":"<html...>"}

    查看所有评论api:
        http://weibo.com/aj/comment/big?_wv=5&id=3451784896742605&max_id=3474003261477621&filter=0&page=2&__rnd=1395231865936
    查看所有转发api:
        http://weibo.com/aj/mblog/info/big?_wv=5&id=3451784896742605&max_id=3560258179526005&filter=0&page=2&__rnd=1395231833403

返回格式::

    {
        "code": "100000",
        "msg": "",
        "data": {
            "html": "...",
            "page": {
                "totalpage": 201,
                "pagenum": 2
            },
            "count": 4005
        }
    }

关键在id，page循环体内递增，爬完判断。

Weibo:

    模块中定义 模拟浏览器登录 的处理类
    
    可以这样用，初始化完成即已登录。

    wb = Weibo(user, password)

日志::

    .. 
        1.2 fix bug [Errno 10054] 这个错误是connection reset by peer.也就是传说的远端主机重置了此连接。
        1.5 可以根据爬评论，爬转发信息，好多天的成果。
        1.6 reviews
'''

from urllib import urlencode,quote
import cookielib, urllib, urllib2, httplib
import os, sys, time
import base64, rsa
import json, re, binascii

import requests
from bs4 import BeautifulSoup

#: 版本 
__version__ = '1.6'
#: 作者
__author__ = 'pythonwood'
#: 日期
__datetime__ = '2014-06-03'
#: 心情
__mood__ = '慢慢乐观，自信，爱。'


cookies = {
'SINAGLOBAL':'7384095699526.369.1401609953245',
'UOR':',,login.sina.com.cn',
'SUBP':'002A2c-gVlwEm1uAWxfgXELuuu1xVxBxA7phgc1UHDv39FD4Xz-6p0HuHY-u_1%3D',
'un':'13750022544@163.com',
'_s_tentry':'weibo.com',
'Apache':'8569682755041.867.1401932422169',
'ULV':'1401932422210:5:5:5:8569682755041.867.1401932422169:1401771921569',
'YF-Page-G0':'ffe43932f05408fcdf32c673d8997f97',
'YF-V5-G0':'fec5de0eebb24ef556f426c61e53833b',
'login_sid_t':'cce6c55fa95bf4a738443acb4d5cf341',
'YF-Ugrow-G0':'062d74e096398759b246e61a81b65c98',
'v5':'5fc1edb622413480f88ccd36a41ee587'
}

headers = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip,deflate,sdch',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'weibo.com',
'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36',
'Cookie':'SINAGLOBAL=7384095699526.369.1401609953245; UOR=,,login.sina.com.cn; _s_tentry=weibo.com; Apache=8569682755041.867.1401932422169; ULV=1401932422210:5:5:5:8569682755041.867.1401932422169:1401771921569; YF-Page-G0=ffe43932f05408fcdf32c673d8997f97; YF-V5-G0=fec5de0eebb24ef556f426c61e53833b; login_sid_t=cce6c55fa95bf4a738443acb4d5cf341; YF-Ugrow-G0=062d74e096398759b246e61a81b65c98; v5=5fc1edb622413480f88ccd36a41ee587; appkey=; SUS=SID-2646808671-1401935853-GZ-g496v-46dabd282689d4c9bf6cd882d0802be9; SUE=es%3Db1cb7e7952848a9e738684e53fb33639%26ev%3Dv1%26es2%3D8ec1c0004d45cbd04ec4532cc0a29731%26rs0%3DMHP%252FfEsDycutNtGjENIH4e5D%252FE3lxfObjVT5E96mPV6xegpZ4fX8qcr3q6yGT3t7LCCfsX9RPoSXz561hKVXUvbunnz9limE5AnZCSkCNqF9kfTBbFygjne4OBIFNwKi3rSV6UsLVkZ0yODLkcPTC29E5uHAJN9mFOUZXgtBT3c%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1401935853%26et%3D1402022253%26d%3Dc909%26i%3D2be9%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D19%26st%3D0%26uid%3D2646808671%26name%3D13750022544%2540163.com%26nick%3D%25E6%25A0%25A1%25E5%259B%25AD%25E7%25BB%258F%25E6%25B5%258E%25E8%25B5%2584%25E8%25AE%25AF%25E5%2593%2588%25E5%2593%2588%26fmp%3D%26lcp%3D; SUB=AejYkRSMERO5GhGZhAtq1D1WVczmGI8%2F1LaVSVHq2XNPhGySbxC%2F6XEyXRq7Jw%2B7dWj%2BjDjAy9bf63N7prkOob1QSspkvsLeYM2POBaSsb%2BLMEl%2F75yL%2BhALAI2Dk8AgdNTr%2B2P%2Bx%2F1Ns0owR%2BbMISE%3D; SUBP=002A2c-gVlwEm1uAWxfgXELuuu1xVxBxA7phgc1UHDv39FD4Xz-6p0HuHY-u_1%3D; ALF=1433471852; SSOLoginState=1401935853; un=13750022544@163.com; page=e2379342ceb6c9c8726a496a5565689e'
}

rootdir = '/media/E/loveq-weibo'

head = ('时间','网址','id','赞','转发','评论')

urls_list = []

SEP = '\t'

def requests_get(url, params=None):
    resp = requests.get(url, params=params, cookies=cookies, headers=headers)
    # print resp.url, params, resp.text[:2000]
    sys.stdout.write('.'); sys.stdout.flush()
    # with open('tmp.html', 'w') as f : f.write(resp.text)
    return resp


def add_urls_list(html):
    def tool(text):
        v1 = text.find('(')
        v2 = text.find(')')
        if 0<=v1 and v1<v2:
            return text[v1+1:v2]
        else:
            return '0'
        
    ret = 0
    bs = BeautifulSoup(html)
    # print bs.prettify()
    for post in bs.find_all('div', class_="WB_feed_datail S_line2 clearfix"):
        # print post.prettify()
        WB_func = post.find_all('div', class_="WB_func clearfix")[-1]  # 技巧
        WB_handle = WB_func.findChild('div', class_='WB_handle')
        WB_from = WB_func.findChild('div', class_='WB_from')
        WB_from_a = WB_from.findChild('a')
        postid = WB_from_a.attrs['name']  # post.mid
        url = u'http://weibo.com' + WB_from_a.attrs['href']
        time = WB_from_a.attrs['title']
        WB_handle_a = WB_handle.findChildren('a')

        zan = tool(WB_handle_a[0].text)
        zhuanfa = tool(WB_handle_a[1].text)
        pinglun = tool(WB_handle_a[3].text)
        if any(postid in i for i in urls_list):
            return ret
        else:
            urls_list.append((time, url, postid, zan, zhuanfa, pinglun))
            ret += 1
    return ret

def get_posts_list(uid, keyword):
    url = 'http://weibo.com/p/aj/mblog/mbloglist'
    # url = 'http://127.0.0.1:8000'
    params = {
        '_wv': '5',
        'domain': '100505',
        'pre_page': '1',
        'page': '1',
        'max_id': '3708816657175473',
        'end_id': '3716789328888062',
        'count': '15',
        'pagebar': '1',
        'max_msign': '',
        'filtered_min_id': '',
        'pl_name': 'Pl_Official_LeftProfileFeed__24',
        'id': '100505%s'%uid,
        'script_uri': '/p/100505%s/weibo'%uid,
        'feed_type': '0',
        'profile_ftype': '1',
        'key_word': keyword,
        'is_search': '1',
        '__rnd': '1401772208635',
    }
    opt = ('pre_page', 'page', 'pagebar')
    n = 1
    while n < 50:
        for sel in ((n-1,n,0),(n,n,0),(n,n,1)):
            params.update(dict(zip(opt,sel)))
            resp = requests_get(url, params)
            rj = resp.json()
            if add_urls_list(rj['data']) == 0: 
                # print sel, resp.url, resp.status_code, len(resp.text) 
                return
        n += 1


def dump(uid, keyword, filename=None):
    if not filename:
        filename = '%s%s.txt'%(keyword,uid)
    with open(filename, 'w') as f:
        f.write(SEP.join(head))
        f.write(os.linesep)
        f.write(os.linesep.join(SEP.join(i) for i in urls_list))
def load(uid, keyword, filename=None):
    if not filename:
        filename = '%s%s.txt'%(keyword,uid)
    if not os.path.isfile(filename):
        return
    fp = open(filename, 'r')
    lines = [line.strip() for line in fp.readlines()]
    for line in lines[1:]:
        urls_list.append(line.split(SEP))

def pull_comment(html):
    ''''''


def main():
    # test = [('床前明月光','1716235922'), ('恭喜发财','1724187070')]
    # test = [(1991027691,'招聘微博'), ('liuyangzhi', '对某大学毕业照片说了两句不中听的话，招来不少年轻人不满')]
    uid, keyword = ('1716235922','床前明月光',)
    get_posts_list(uid, keyword)
    dump(uid, keyword)

if __name__ == '__main__':
    ''''''
    # main()
