#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
文档生成用sphinx

模块:weibo
    一个微博爬虫模块。作者pythonwood。

    起因是为了看《一些事一些情》的微博评论更方便。

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

from datetime import datetime

import requests
from bs4 import BeautifulSoup

#: 版本 
__version__ = '1.6'
#: 作者
__author__ = 'pythonwood'
#: 日期
__datetime__ = '2014-06-05'
#: 心情
__mood__ = '慢慢乐观，自信，爱。'


cookies = {
}

headers = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip,deflate,sdch',
'Accept-Language':'zh-CN,zh;q=0.8',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Host':'weibo.com',
# 'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36',
# 'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
'User-Agent':'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0) ',
'Cookie':'SINAGLOBAL=7384095699526.369.1401609953245; UV5=usrmdins312_177; _s_tentry=-; Apache=3144713302608.5796.1402021756413; ULV=1402021756513:7:7:7:3144713302608.5796.1402021756413:1401941181968; login_sid_t=19cccba123e99530d32ecc8aa90c7ddd; UUG=usr1473; UOR=,,login.sina.com.cn; SUS=SID-2646808671-1402021768-GZ-rok6h-f6993276b17e1564dc1046e7228ec8ba; SUE=es%3Db8f06351ec5811f36fc02b3bb1fdc4d3%26ev%3Dv1%26es2%3Dc9f04600f9e22f7a99c43deed77dcf2a%26rs0%3DUOr%252BKZbpXX3%252BimOs9%252FWcF%252FW5bXUWdoP9HhwNqkj6ncf97hRYkZ2x5Y30Vkf37BtiVzAtTMYYjB%252FJJVRooltkBIUfn%252F8cA5GMC3z5QHOEtlJ6pGjlaawbguINluU1iwWpbJNaekfsC4UAuFgHlYlRRvcGGT%252FgZHoQh%252FZtEycMUh8%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1402021768%26et%3D1402108168%26d%3Dc909%26i%3Dc8ba%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D2646808671%26name%3D13750022544%2540163.com%26nick%3D%25E6%25A0%25A1%25E5%259B%25AD%25E7%25BB%258F%25E6%25B5%258E%25E8%25B5%2584%25E8%25AE%25AF%25E5%2593%2588%25E5%2593%2588%26fmp%3D%26lcp%3D; SUB=Aear4qsE%2F8W4zvauaRmMyImy9QnaadZvzuYTBlliLQkhmbRilZL1KLc9Gb2tABT9CZDYZO14E1ouhrSpdgF1X3bW%2FJ0ThrYfrEUM%2FKS0vuc8y8Wy4aE%2BhDVwJVXoBrEs54MfWeDdl98Joa9Yvnfj0N4%3D; SUBP=002A2c-gVlwEm1uAWxfgXELuuu1xVxBxA7phgc1UHDv39FD4Xz-6p0HuHY-u_1%3D; ALF=1433557767; SSOLoginState=1402021768; un=13750022544@163.com; wvr=5; UV5PAGE=usr513_172'
}

html_tpl = \
u''' <!DOCTYPE html>
<html lang="zh-cn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="python应用，一些事一些情微博评论。">
<meta name="author" content="JNU, pythonwood, 582223837@qq.com, 2014-06">
<title> %s </title>
<link rel="stylesheet" href="http://cdn.bootcss.com/twitter-bootstrap/3.0.3/css/bootstrap.min.css">
<style text="text/css"> body { padding-top: 50px; } </style>
</head>
<body data-spy="scroll" data-target="#mynav">
<nav id="mynav" class="navbar navbar-default navbar-inverse navbar-fixed-top" role="navigation">
  <div class="container">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#mynav-collapse">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="#">LoveQ</a>
    </div>
    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="mynav-collapse">
      <ul class="nav navbar-nav navbar-left">
        <li class="active"><a href="#">0</a></li>
        %s
      </ul>
    </div><!-- /.navbar-collapse -->
  </div>
</nav>
<div class="container">
<h3> %s </h3>
<ul class="list-unstyled">
%s
</ul>
</div>
<script src="http://cdn.bootcss.com/jquery/1.10.2/jquery.min.js"></script>
<script src="http://cdn.bootcss.com/twitter-bootstrap/3.0.3/js/bootstrap.min.js"></script>
<script type="text/javascript">
$(function(){
    $('a[href^="/"]').each(function(){this.href='http://weibo.com'+$(this).attr('href');});
    $('ul.list-unstyled>li>img[src^="http://tp"]').each(function(){$(this).click(function(){var name=$(this).next('a').text().trim(); $('ul.list-unstyled li').hide(); $('ul.list-unstyled li:contains("'+name+'")').show();});});
    $('a.navbar-brand').click(function(){$('ul.list-unstyled li').show();});
	var x = 10;
	var y = 20;
	$('ul.list-unstyled>li>img[src^="http://tp"]').mouseover(function(e){
		$("<div id='tooltip'><img src='"+ this.src.replace('\/50\/', '/180/') +"'/><\/div>").insertBefore('ul.list-unstyled');						 
		$("#tooltip") .css({ "position": "absolute", "top": (e.pageY+y) + "px", "left":  (e.pageX+x)  + "px" }).show("fast");	  //设置x坐标和y坐标，并且显示
    }).mouseout(function(){
		$("#tooltip").remove();	 //移除 
    }).mousemove(function(e){
		$("#tooltip") .css({ "position": "absolute", "top": (e.pageY+y) + "px", "left":  (e.pageX+x)  + "px" });
	});
})
</script>
</body>
</html>
'''




def requests_get(url, params=None):
    resp = requests.get(url, params=params, cookies=cookies, headers=headers)
    # print resp.url, params, resp.text[:2000]
    sys.stdout.write('.'); sys.stdout.flush()
    # with open('tmp.html', 'w') as f : f.write(resp.text)
    return resp
def requests_json(url, params=None, limit=5):
    n = 0
    while n<5:
        try:
            resp = requests_get(url, params=params)
            rj = resp.json()
            return rj
        except ValueError as e:
            sys.stdout.write('E');sys.stdout.flush()
            print >> sys.stderr, e, resp.url, resp.status_code
            with open('tmp.html', 'w') as f: f.write(resp.text.encode('utf-8'))
        except Exception as e:
            print e
        n += 1
    raise ValueError('trys %s times failed'%n)

def add_urls_list(urls_list, html):
    def tool(text):
        v1 = text.find('(')
        v2 = text.find(')')
        if 0<=v1 and v1<v2:
            return text[v1+1:v2]
        else:
            return '0'
    ret = []
    bs = BeautifulSoup(html)
    for post in bs.find_all('div', class_="WB_feed_datail S_line2 clearfix"):
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
            break
        else:
            #: fix bug encoding #:ret.append((time, url, postid, zan, zhuanfa, pinglun))
            ret.append([i.encode('utf-8') for i in (time, url, postid, zan, zhuanfa, pinglun)])
    return ret

def get_posts_list(urls_list, uid, keyword, limit_page=1000):
    ret = []
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
    while n < limit_page:
        for sel in ((n-1,n,0),(n,n,0),(n,n,1)):
            params.update(dict(zip(opt,sel)))
            # resp = requests_get(url, params)
            # rj = resp.json()
            rj = requests_json(url, params)
            adds = add_urls_list(urls_list, rj['data'])
            if adds:
                ret.extend(adds)
            else:
                # print sel, resp.url, resp.status_code, len(resp.text)
                break
        else:
            n += 1
            continue
        break
    print 'update %s new items' % len(ret)
    return ret


#: 头
head = ('关键字','时间','网址','id','赞','转发','评论')
# dt, url, id, zan, zhuanfa, pinglun

#: 分隔符 SEP = '\t'
def dump(urls_list, filename='', uid='', keyword='', SEP = '\t'):
    if not filename:
        filename = '%s%s.txt'%(keyword,uid)
    with open(filename, 'w') as f:
        f.write(SEP.join(head))
        f.write(os.linesep)
        f.write(os.linesep.join(SEP.join(i) for i in urls_list))
    return filename
def load(filename='', uid='', keyword='', SEP = '\t'):
    urls_list = [] 
    if not filename:
        filename = '%s%s.txt'%(keyword,uid)
    if not os.path.isfile(filename):
        print 'filename: %s do not exist' % filename
        return
    fp = open(filename, 'r')
    lines = [line.strip() for line in fp.readlines()]
    # for line in lines[-1:0:-1]:
    for line in lines[1:]:
        urls_list.append(line.split(SEP))
    return urls_list




def save(html, filename, title=u''):
    '''保存'''
    bs = BeautifulSoup(html)
    items = []
    nav_items = []
    dls = bs.find_all('dl')
    for i, dl in enumerate(dls):
        i += 1
        img = dl.dt.a.img.extract()
        del img['usercard']
        del img['alt']

        dd = dl.dd.extract()
        del dd.a['usercard']
        del dd.a['title']
        dd.find('div', class_="info").decompose()
        pro = dd.find('div', class_="WB_media_expand repeat S_line1 S_bg1")
        if pro:
            pro.decompose()
        dd.find('span', class_="S_txt2").unwrap()

        dd.name = 'li'
        dd.insert(0, '#%s'%i)
        dd.insert(0, img)
        if i%100 == 0:
            dd['id'] = "t%s"%i
            nav_items.append(u'<li class=""><a href="#t%s">%s</a></li>' % (i,i/100))
        items.append(dd.prettify())
    h = html_tpl % (title, u'\n'.join(nav_items), title, u'\n'.join(items))
    with open(filename, 'w') as f:
        f.write(h.encode('utf-8'))
    return len(h)
        

def pull(urls_list, keyword, dirname='/media/E/loveq/weibo/', limit_page=1000):
    def pt(dt):
        return dt.strftime('%H:%M:%S')
    def sizeof_fmt(num):
        for x in ['bytes','KB','MB','GB','TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
    url_tpl = 'http://weibo.com/aj/comment/big?_wv=5&id=%s&max_id=3718116146669325&filter=0&page=%s&__rnd=1401970176137'
    dirname_all = ' '.join(os.listdir(dirname))
    for it in urls_list:
        # add keyword in urls_list
        dt, url, postid, zan, zhuanfa, pinglun = tuple(it)
        filename = '%s%s%s%s.html' % (dt.replace(' ','_').replace(':','-'), keyword, pinglun, '评论')
        filepath = os.path.join(dirname, filename)
        testname = '%s%s'%(filename[:16],keyword)
        # if os.path.isfile(testname): # 宽松点
        if testname in dirname_all:
            print '%s exist' % filename
            continue
        start = datetime.now()
        print '[%s start] %s' % (pt(start), filepath)
        n = 1
        tag_data = ''
        while n<limit_page:
            # resp = requests_get(url, params)
            # rj = resp.json()
            rj = requests_json(url_tpl%(postid,n))
            jn = rj['data']
            tag_data += jn['html']
            jn = jn['page']
            if jn['totalpage'] == jn['pagenum']:
                # print n, resp.url, resp.status_code, len(resp.text), jn['totalpage'], jn['pagenum']
                break
            n += 1
        title = '%s %s %s%s'%(dt,keyword,pinglun,'评论')
        filesize = save(tag_data, filepath, title.decode('utf-8'))
        done = datetime.now()
        secs = (done-start).seconds
        leng = len(tag_data)
        if secs > 0: # figbug: ZeroDivisionError
            speed = sizeof_fmt(leng/secs)
            print '\n[%s done] %s used %ss (%s pages %s avg %s/s)' % (pt(done), sizeof_fmt(filesize), secs, n, sizeof_fmt(leng), speed) 


def main():
    test = [('床前明月光','1716235922'), ('恭喜发财','1724187070')]
    # test = [(1991027691,'招聘微博'), ('liuyangzhi', '对某大学毕业照片说了两句不中听的话，招来不少年轻人不满')]
    for keyword,uid in test:
        try:
            filepath = '/media/E/loveq/%s-%s' % (uid, keyword)
            #: 微博列表,按时间倒序的
            urls_list = []
            if os.path.isfile(filepath):
                urls_list = load(filepath)
            adds = get_posts_list(urls_list, uid, keyword) # urls_list 用于比较而已
            urls_list = adds + urls_list
            dump(urls_list, filepath)

            dirname = '/media/E/loveq/weibo'
            pull(urls_list,keyword, dirname)
        except KeyboardInterrupt as e:
            print e
            continue

if __name__ == '__main__':
    ''''''
    main()
