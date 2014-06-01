#!/usr/bin/env python
# -*- coding: utf-8 -*-

# windows 也会相应 # -*- coding: utf-8 -*- @2014-02-26
# '\xef\xbb\xbf' 是 BOM，在文件头表示utf-8编码，python没有跳过。Windows中
# 由于BOM作怪，用来很久一天多才完成，现在深夜1:30，我恨微软。

# 2.1 修复没下载完全部评论就停的bug

from weibo import Weibo
from urllib import urlencode,quote
import re, json
import os,sys,time

# Weibo是登录拿cookie 依赖rsa
wb = Weibo('13750022544@163.com', '19920616')

hh = '''<!DOCTYPE html>
<html lang="zh-cn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="python应用，一些事一些情微博评论。">
<meta name="author" content="pythonwood 2014">
<title>%s</title>
<link rel="stylesheet" href="http://cdn.bootcss.com/twitter-bootstrap/3.0.3/css/bootstrap.min.css">
</head>
<body>
<div class="container">
<ul class="list-unstyled">'''
hf = '''</ul></div>
<script src="http://cdn.bootcss.com/jquery/1.10.2/jquery.min.js"></script>
<script type="text/javascript">
$('a[usercard]').each(function(){this.href='http://weibo.com'+this.href.substring(this.href.lastIndexOf('/'))})
</script>
</body>
</html>'''

# 关键字搜索特定微博，获取下载url
def comment(keyword,uid):

    fn = keyword+'.txt'
    fn = fn.decode('utf-8')

    bef = ''
    latest = ''
    if os.path.isfile(fn):
        with open(fn, 'r') as f:
            bef = f.readlines()
            if bef: latest = bef[0]
    # print latest
        

    # 关键字搜索
    kw = quote(keyword)
    url = 'http://weibo.com/p/aj/mblog/mbloglist?domain=100505&pre_page=%s&page=%s&count=15&pagebar=%s&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__22&id=100505'+uid+'&script_uri=/p/100505'+uid+'/weibo&feed_type=0&profile_ftype=1&key_word=%s&is_search=1&__rnd=1392289857878'
        
    # 编译正则，加快匹配
    t = re.compile(r'<a suda-data="key=smart_feed&value=time_sort_comm".*?评论\(([0-9]+)\).*?name=([0-9]+).*?(/%s/[^?]+).*?"([0-9]{4}-[0-9]{1,2}-[0-9]{1,2}) ([0-9]{1,2}:[0-9]{1,2})"'%uid, re.S)

    dl = []
    def get(url):
        sys.stdout.write('.')
        
        h = json.loads(wb.urlopen(url).read())['data'].encode('utf-8')
        # with open('tmp.html', 'w') as f: f.write(h)
        
        m = t.findall(h)
        # [('1917', '3630155224455586', '/1716235922/AcEtsiH6i', '2013-10-5', '21:31')]
        if not m:
            raise Exception('for break')
        
        for i in range(len(m)):
            j = m[i]
            # 发现相同应该停止
            if j[1] in latest:
                raise Exception('for break')
            dl.append(("%s_%s%s%s"%(j[3],j[4],keyword,j[0]), j[1], j[2]))
            # 2013-10-5_21:31床前明月光1917	3630155224455586	/1716235922/AcEtsiH6i

    n = 1
    while(True):
        try:
            get(url % (n-1,n,0,kw))
            get(url % (n,n,0,kw))
            get(url % (n,n,1,kw))
            n += 1
        except:
            break

    print "update %s url in %s" % (len(dl), fn)

    if dl: # bug without this line!
        with open(fn, 'w') as f:
            f.write('\n'.join('\t'.join(i) for i in dl)+'\n'+''.join(bef))

    # start_pull(keyword)


def start_pull(keyword):
    fn = keyword + '.txt'
    fn = fn.decode('utf-8')
    
    dl = []
    with open(fn, 'r') as f:
        # '\xef\xbb\xbf' 是 BOM，在文件头表示utf-8编码，python没有跳过。Windows中
        for line in f:
            if line.startswith('\xef\xbb\xbf'):
                line = line[3:]
            tmp = line.split('\t') # 分解后tmp[0]含'\xef\xbb\xbf'而无法作为文件等等，真他妈的微软，Fuck!
            # print tmp # '\xef\xbb\xbf'
            if len(tmp)>=2: # bug without this line
                dl.append(tmp)
    # print dl

    # 判断文件是否存在，很难
    # 'comment/2013' 的 '/2'中间还有个鬼符号，导致识别错误。IDLE测试：Unsupported characters in input
    # 个鬼符号原来是'\xef\xbb\xbf'
    # fs = '\n'.join(os.listdir('comment/'))
    # for i in dl:
    #     print fs, i[0][:i[0].find(':')], i[0][:i[0].find(':')] in fs
    #     if i[0][:i[0].find(':')] in fs:
    #         continue
    
    # fs = list(os.listdir('comment/'))
    # for i in dl:
    #     test = i[0][:i[0].find(':')]
    #     print test
    #     if any(test in j for j in fs):
    #         continue

    for i in dl:

        before = time.time()

        # windows 下文件名不可以有:
        filename = 'comment/'+i[0].replace(':','-')+'.html'
        filename = filename.decode('utf-8')
        if os.path.isfile(filename):
            continue

        sys.stdout.write( "download and make " + filename )

        url = 'http://weibo.com/aj/comment/big?_wv=5&id='+i[1]+'&max_id=4651849175081847&filter=0&page=%s&__rnd=1386153222398'
        body = pull_comment(url,wb)

        with open(filename, 'w') as f:
            f.write(hh % i[0])
            f.write(body)
            f.write(hf)

        time_used = time.time()-before
        print "\ndone(%sK:%s秒)" % (os.path.getsize(filename)/1024, round(time_used, 1))


def pull_comment(url, opener):
    rstr = ''
    pagenum = 1
    count = 1
    rb = re.compile(r'<dt>(.*?)</dt>.*?<dd>.*?(<a.*?</a>).*?(：.*?)<span.*?>([^<]*)', re.S)
    maxcount = 0
    while(True):
        sys.stdout.write('.')
        try: 
            j = json.loads(opener.urlopen(url % pagenum).read())
        except Exception as e:
            sys.stdout.write(str(e))
            # sys.stdout.write('O')
            continue
        d = j['data']
        m = rb.findall(d['html'].encode('utf-8'))
        ### 2.1
        if pagenum==1:
            maxcount=d['count']
        if not m and maxcount-count > 100: # 设置100个可丢失额
            print maxcount, count, url % pagenum
#            continue
        for k in m:
            rstr += '<li>' + '\n'.join(k)+'.%d</li>\n'%count
            count += 1
        d = d['page']
        if not m or d['pagenum'] == d['totalpage'] or pagenum >= 500:  # 设置上限500面
            break
        pagenum += 1
    return rstr




if __name__ == '__main__':
    comment('床前明月光','1716235922')
    comment('恭喜发财','1724187070')

    try:start_pull('床前明月光')
    except KeyboardInterrupt as e: print e
    try:start_pull('恭喜发财')
    except KeyboardInterrupt as e: pass
