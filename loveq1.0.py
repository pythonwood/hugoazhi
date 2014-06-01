#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weibo import Weibo
from urllib import urlencode,quote
import re, json
import os,sys,time
from bs4 import BeautifulSoup

wb = Weibo('13750022544@163.com', '19920616')

def comment(keyword,uid):
    kw = quote(keyword)
    url = 'http://weibo.com/p/aj/mblog/mbloglist?domain=100505&pre_page=%s&page=%s&count=15&pagebar=%s&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__22&id=100505'+uid+'&script_uri=/p/100505'+uid+'/weibo&feed_type=0&profile_ftype=1&key_word=%s&is_search=1&__rnd=1392289857878'

    # t = re.compile(r'%s.*?url=http://weibo.com/.*?转发\(([0-9]+)\).*?评论\(([0-9]+)\).*?<a name=([^ ]+) target="_blank" href="(/%s/[^?]+).*? ([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2})'%(keyword, uid), re.S)
    t = re.compile(r'<a suda-data="key=smart_feed&value=time_sort_comm".*?评论\(([0-9]+)\).*?name=([0-9]+).*?(/%s/[^?]+).*?"([0-9]{4}-[0-9]{1,2}-[0-9]{1,2}) ([0-9]{1,2}:[0-9]{1,2})"'%uid, re.S)

    dl = []
    def get(url):
        h = json.loads(wb.urlopen(url).read())['data'].encode('utf-8')
        m = t.findall(h)
        # [('1917', '3630155224455586', '/1716235922/AcEtsiH6i', '2013-10-5', '21:31')]
        if not m:
            raise Exception('for break')
        dl.extend(m)
    n = 1
    while(True):
        try:
            get(url % (n-1,n,0,kw))
            get(url % (n,n,0,kw))
            get(url % (n,n,1,kw))
            n += 1
        except:
            break

    l = len(dl)
    for i in range(l):
        j = dl[i]
        # 2013-10-5_21:31床前明月光1917	3630155224455586	/1716235922/AcEtsiH6i
        dl[i] = ("%s_%s%s%s"%(j[3],j[4],keyword,j[0]), j[1], j[2])

    with open('%s.txt'%keyword, 'w') as f:
        f.write('\n'.join('\t'.join(i) for i in dl))

    # download_worker(keyword)


def download_worker(keyword):
    dl = []
    with open('%s.txt'%keyword, 'r') as f:
        for line in f:
            dl.append(line.split('\t'))

    for i in dl:
        if i[0][:-3] in ' '.join(os.listdir('comment/')):
            continue
        url = 'http://weibo.com/aj/comment/big?_wv=5&id='+i[1]+'&max_id=4651849175081847&filter=0&page=%s&__rnd=1386153222398'
        filename = 'comment/'+i[0]+'.html'
        print "download and make --> %s..." % filename
        f = open(filename, 'w')
        f.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n')
        pagenum = 1
        before = time.time()
        while(True):
            html = ''
            json_VE = True
            while json_VE:
                try:
                    json_data = json.loads( wb.urlopen(url % pagenum).read() )[u'data']
                    html = BeautifulSoup(json_data[u'html']).body.encode('utf-8')
                    json_VE = False
                except ValueError as e:
                    print e
            f.write(html)
            f.flush()
            if pagenum == json_data[u'page'][u'totalpage'] or pagenum >= 500:  # 设置上限500面
                break
            pagenum += 1
        f.close()
        time_used = time.time()-before
        print "download and make --> %s......%sK:%s秒" % (filename,os.path.getsize(filename)/1024, round(time_used, 1))
        # print date, " download used ", int(time_used), "s ", round(os.path.getsize(filename) / time_used / 1000, 1), "kb/s" 




if __name__ == '__main__':
    # comment('床前明月光','1716235922')
    # comment('恭喜发财','1724187070')
    download_worker('床前明月光')
    download_worker('恭喜发财')
