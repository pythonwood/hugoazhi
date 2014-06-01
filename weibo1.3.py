#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 登陆成功 实测2014-02-13
# 面向对象封装成Weibo类
# 参考：一枚菜鸟的学习笔记 2013-03-10 http://blog.csdn.net/monsion/article/details/8656690
'''
模块:weibo
    一个微博爬虫模块。作者pythonwood。
    起因是为了看《一些事一些情》的微博评论更方便。

微博探测笔记：
    根据用户名字找id，源文件html嵌入了JS代码$CONFIG['oid']='1093974672'; 

    查看所有评论api:
        http://weibo.com/aj/comment/big?_wv=5&id=3451784896742605&max_id=3474003261477621&filter=0&page=2&__rnd=1395231865936
    查看所有转发api:
        http://weibo.com/aj/mblog/info/big?_wv=5&id=3451784896742605&max_id=3560258179526005&filter=0&page=2&__rnd=1395231833403
    返回格式：
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

Weibo.reset(user, pw):
    重置用户，密码

Weibo.search_post(user,keyword,filename=None):
    搜索某用户含关键词微博，信息保存到 关键词_id.txt
    例如搜索hugo的一些事一些情的含“床前明月光”微博。保存在“床前明月光_1716235922.txt”中
    文件每行格式一样：
    2014-03-09_23:04恭喜发财289(\tab)3686348718617570(\tab)/1724187070/AAek7A9P4

Weibo.pull_comment(id, filename):
    将id对应微博的评论下载到本地filename文件中，并简化美化。

Weibo.pull_comment_worker(dirname):
    下载符合格式的文件中的每条记录。

Weibo.pull_forward(id, filename):
    将id对应微博的转发下载到本地filename文件中，并简化美化。

Weibo.pull_forward_worker(filename):
    下载符合格式的文件中的每条记录。

1.2 fix bug [Errno 10054] 这个错误是connection reset by peer.也就是传说的远端主机重置了此连接。
'''

from urllib import urlencode,quote
import cookielib, urllib, urllib2, httplib
import os, sys, time
import base64, rsa
import json, re, binascii

# 自定义返回码处理过程
class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    '''used to make opener'''
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result


class Weibo:
    '''
    Weibo:
    '''
    # ua = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    ua = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:27.0) Gecko/20100101 Firefox/27.0'}
    def __init__(self, user, pw, debug=False):
        '''
        you can make:
        wb = Weibo(user, password)
        '''
        d = httplib.HTTPConnection.debuglevel
        if debug:
            httplib.HTTPConnection.debuglevel = 1

        # 制造可处理Cookie类，使用自定义处理过程
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()), DefaultErrorHandler)
        self.reset(user,pw)
        # 复原
        if debug:
            httplib.HTTPConnection.debuglevel = d

    def reset(self, user, pw):
        '''重置用户，密码'''
        self.user = user
        self.pw = pw
        return self.login()

    def login(self):
        '''登录过程，初始化时调用，返回self'''
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % self.user
        #: e.g 'sinaSSOController.preloginCallBack({"retcode":0,"servertime":1392274484,"pcid":"gz-58593947d0295e6aecc605897b4211ad6e3e","nonce":"HMOD0L","pubkey":"EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443","rsakv":"1330428213","exectime":0})
        soc = self.urlopen(url)
        data = json.loads(soc.read()[35:-1])
        soc.close()
        #: 第一次http请求， 获取有用信息，将与加密后密码一同post
        servertime, nonce, pubkey, rsakv = str(data['servertime']), data['nonce'], data['pubkey'], data['rsakv']
        key = rsa.PublicKey(int(pubkey,16), 65537)
        sp = rsa.encrypt(str(servertime) + '\t' + str(nonce) + '\n' + str(self.pw), key)
        #: 用户名url编码,base64加密
        su = base64.encodestring(urllib.quote(self.user))[:-1]
        sp = binascii.b2a_hex(sp)
        postdata = {
                'entry': 'weibo',
                'gateway': '1',
                'from': '',
                'savestate': '7',
                'userticket': '1',
                'ssosimplelogin': '1',
                'vsnf': '1',
                'vsnval': '',
                'su': su,
                'service': 'miniblog',
                'servertime': servertime,
                'nonce': nonce,
                'pwencode': 'rsa2',
                'sp': sp,
                'encoding': 'UTF-8',
                'prelt': '115',
                'rsakv': rsakv,
                'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                'returntype': 'META'
                }
        req = urllib2.Request(
                url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)',
                data = urllib.urlencode(postdata),
                headers = Weibo.ua
                )
        o = self.opener.open(req)
        h = o.read()
        o.close()
        #e.g location.replace("http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&ssosavestate=1394872359&ticket=ST-MjY0NjgwODY3MQ==-1392280359-gz-C29D9682D3DE6B9174BA3A502294B24A&retcode=0");
        #: 第二次http请求 已经成功一半，还要访问几个页面。
        o = self.urlopen(re.search('location\.replace\("(.*)"\);', h).group(1))
        #: e.g parent.sinaSSOController.feedBackUrlCallBack({"result":true,"userinfo":{"uniqueid":"2646808671","userid":null,"displayname":"\u6821\u56ed\u7ecf\u6d4e\u8d44\u8baf\u54c8\u54c8","userdomain":"?wvr=5&lf=reg"},"redirect":"http:\/\/weibo.com\/guide\/welcome"});
        #: 第三次http请求，有可能返回要验证码。
        if "\u4e3a\u4e86\u60a8\u7684\u5e10\u53f7\u5b89\u5168\uff0c\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801" in o.read():
            raise Exception("为了您的帐号安全，请输入验证码")
        #: 成功
        o.close() # for [Errno 10054] 远程主机强迫关闭了一个现有的连接。
        return self


    def win_bom_fix(self, fileread):
        '''该死的windows，杀千刀'''
        if fileread.startswith('\xef\xbb\xbf1'):
            return fileread[3:]
        return fileread

    def search_post(self,user,keyword,filename=None):
        '''
        搜索某用户含关键词微博，信息保存到 关键词_id.txt
        例如搜索hugo的一些事一些情的含“床前明月光”微博。保存在“床前明月光_1716235922.txt”中
        文件每行格式一样：
        2014-03-09_23:04恭喜发财289(\tab)3686348718617570(\tab)/1724187070/AAek7A9P4

python socket.error: [Errno 10054] 远程主机强迫关闭了一个现有的连接。
这个错误是connection reset by peer.也就是传说的远端主机重置了此连接。
原因可能是socket超时时间过长；也可能是request = urllib.request.urlopen(url)之后，
没有进行request.close()操作；也可能是没有sleep几秒，导致网站认定这种行为是攻击。
        '''
        if filename==None:
            filename = '%s_%s.txt' % (keyword, user)
        ufn = filename.decode('utf-8')
        if type(user) is str:
            nickname = str(user)
            soc = self.urlopen('http://weibo.com/'+nickname)
            h = soc.read()
            soc.close()
            uid = re.search(r"\$CONFIG\['oid'\]='(\d+)';", h).group(1)
            uid = int(uid)
        else:
            uid = user

        latest = ''
        if os.path.isfile(ufn):
            with open(ufn, 'r') as f:
                latest = f.readline().strip()
                latest = self.win_bom_fix(latest)

        # 关键字搜索，注意中文会变成很多%s
        kw = quote(keyword)
        tpl = 'http://weibo.com/p/aj/mblog/mbloglist?domain=100505&pre_page=%s&page=%s&count=15&pagebar=%s&max_msign=\
&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__22&id=100505%s&script_uri=/p/100505%s/weibo&feed_type=0&\
profile_ftype=1&key_word=%s&is_search=1&__rnd=1392289857878' % ('%s', '%s', '%s', uid, uid, '%s') # not kw hear
            
        # 编译正则，加快匹配
        # t = re.compile(r'<a suda-data="key=smart_feed&value=time_sort_comm".*?评论\(([0-9]+)\).*?name=([0-9]+).*?(/%s/[^?]+).*?"([0-9]{4}-[0-9]{1,2}-[0-9]{1,2}) ([0-9]{1,2}:[0-9]{1,2})"'%uid, re.S)
        t = re.compile(r'loc=profile.*?</em>\(?(\d*)\)</a>.*?转发\(?(\d*)\).*?收藏.*?评论\(?(\d*)\).*?'
	   '<a name=(\d+) target="_blank" href="(.*?)\?mod=weibotime" title="(.*?) (.*?)"', re.S)
        #: [('38', '91', '1150', '3680888619802317', '/1716235922/AxWhvF81T', '2014-02-22', '21:28')]
        #: 赞，转发，评论, postid，网址(转发加?type=repost)，日期，时间

        # 重构了这段代码。好多了！ 2014-03-20 (论pytohn循环体后面的else的作用！) 
        dl = []
        n = 1
        while(True):
            for i in [(n-1,n,0,kw), (n,n,0,kw), (n,n,1,kw)]:
                while(True):
                    try:
                        soc = wb.urlopen(tpl % i)
                        h = json.loads(soc.read())['data'].encode('utf-8')
                        soc.close()
                        # with open('tmp%s.html'%n, 'w') as f: f.write(h)
                        sys.stdout.write('.')
                        break
                    except Exception as e:
                        sys.stdout.write(str(e))
                        continue
                
                m = t.findall(h)
                #: [('38', '91', '1150', '3680888619802317', '/1716235922/AxWhvF81T', '2014-02-22', '21:28')]
                ext = [j for j in m if j[3] not in latest]
                dl.extend(ext)
                if len(ext)<len(m) or h.find('<span>正在加载中，请稍候...</span>')==-1:
                    break
            else:
                n += 1
                continue
            break


        if latest:
            with open(ufn, 'r') as f:
                before_data = self.win_bom_fix(f.read())
                if dl: # bug without this line!
                    with open(ufn, 'w') as ff:
                        ff.write('\n'.join('\t'.join(i) for i in dl)+'\n'+before_data)
                print "update %s url in %s" % (len(dl), filename)
        elif dl:
            with open(ufn, 'w') as f:
                f.write('\n'.join('\t'.join(i) for i in dl))
            print "write %s url in %s" % (len(dl), filename)

        return filename #self
    # search_comment() end



    def pull_comment(self,postid):
        '''id -> list of comment'''
        url = 'http://weibo.com/aj/comment/big?_wv=5&id=%s&max_id=4751849175081847&filter=0&page=%s&__rnd=1388853222398' % (postid, '%s')
        r = []
        pagenum = 1
        rb = re.compile(r'<dt>(.*?)</dt>.*?<dd>(.*?</a>)(.*?)<span class="S_txt2">(.*?)</span>', re.S)
        #: 图片，个人主页， 留言，时间
        while(True):
            try:
                soc = self.urlopen(url % pagenum)
                j = json.loads(soc.read())
                soc.close()
                sys.stdout.write('.')
            except Exception as e:
                sys.stdout.write(str(e))
                continue

            d = j['data']
            m = rb.findall(d['html'].encode('utf-8'))
            r.extend(m)
            d = d['page']
            if d['pagenum'] == d['totalpage'] or pagenum >= 500:  # 设置上限500页
                break
            pagenum += 1
        
        return r
        

    def pull_comment_worker(self, filename, dirname='comment/'):
        '''下载符合格式的文件中的每条记录。将id对应微博的评论下载到本地filename文件中，并简化美化。'''

        keyword = filename.split('_')[0]        
        ufn = filename.decode('utf-8')
        #: unicode 文件名跨平台，才不乱码
        
        with open(ufn, 'r') as f:
            dl = f.readlines()
            dl[0] = self.win_bom_fix(dl[0])
        
        dl = [i.split('\t') for i in dl]

        tpl = '''
<!DOCTYPE html>
<html lang="zh-cn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="python应用，一些事一些情微博爬虫。">
<meta name="author" content="pythonwood 2014">
<title>%s</title>
<link rel="stylesheet" href="http://cdn.bootcss.com/twitter-bootstrap/3.0.3/css/bootstrap.min.css">
</head>
<body>
<div class="container">
<h3>%s<small>--pythonwood</small></h3>
<ul class="list-unstyled">
%s
</ul>
</div>
<script src="http://cdn.bootcss.com/jquery/1.10.2/jquery.min.js"></script>
<script type="text/javascript">
$('a[usercard]').each(function(){this.href='http://weibo.com'+this.href.substring(this.href.lastIndexOf('/'))})
</script>
</body>
</html>'''

        for i in dl:
            before = time.time()

            #: [('38', '91', '1150', '3680888619802317', '/1716235922/AxWhvF81T', '2014-02-22', '21:28')]
            # windows 下文件名不可以有:
            win_fix = "%s_%s" % (i[5], i[6].replace(':','-'))
            _filename = "%s%s%s%s%s.html" % (dirname, keyword, win_fix, '评论', i[2])
            ufilename = _filename.decode('utf-8')
            #: unicode 文件名跨平台，才不乱码
            if os.path.isfile(ufilename):
                continue
            sys.stdout.write( ufilename )

            data = self.pull_comment(i[3])

            for j in range(len(data)):
                data[j] = '%s.%s' % ('\n'.join(k.strip() for k in data[j]),j+1)
            html = '<li>%s</li>' % ('</li>\n<li>'.join(data))
            html = tpl % (_filename,_filename,html)
            with open(ufilename, 'w') as f:
                f.write(html)

            time_used = time.time()-before
            print "\nDone: *** %s命中，%sKB，%s秒 ***" % (len(data),os.path.getsize(ufilename)/1024, round(time_used, 1))

    def pull_forward(self, postid):
        '''id -> list of forword info'''

    def pull_forward_worker(self, filename):
        '''下载符合格式的文件中的每条记录。将id对应微博的评论下载到本地filename文件中，并简化美化'''
        

            

    def urlopen(self, url):
        if not url.lower().startswith('http://'):
            url = 'http://' + url
        req = urllib2.Request(
                url = url,
                headers = Weibo.ua
                )
        return self.opener.open(req)


if __name__ == '__main__':
    wb = Weibo('13750022544@163.com', '19920616', debug=True)
    
    test = [(1991027691,'招聘微博'), ('liuyangzhi', '对某大学毕业照片说了两句不中听的话，招来不少年轻人不满')]
    fnlist = []
    for i in test:
        fn = wb.search_post(i[0], i[1])
        fnlist.append(fn)
    for i in fnlist:
        try: wb.pull_comment_worker(i)
        except KeyboardInterrupt as e: sys.stdout.write(str(e))

