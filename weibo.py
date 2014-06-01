#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 登陆成功 实测2014-02-13
# 面向对象封装成Weibo类
# 参考：一枚菜鸟的学习笔记 2013-03-10 http://blog.csdn.net/monsion/article/details/8656690

import cookielib, urllib, urllib2, httplib
import os, sys
import base64, rsa
import json, re, binascii
'''
weibo:
'''

# 自定义返回码处理过程
class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
    def http_error_default(self, req, fp, code, msg, headers):
        result = urllib2.HTTPError(
            req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result


class Weibo:
    '''
    Weibo:
    '''
    ua = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    def __init__(self, user, pw, debug=False):
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
        self.user = user
        self.pw = pw
        return self.login()

    def login(self):
        # 用户名url编码,base64加密
        su = base64.encodestring(urllib.quote(self.user))[:-1]
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % self.user
        #e.g 'sinaSSOController.preloginCallBack({"retcode":0,"servertime":1392274484,"pcid":"gz-58593947d0295e6aecc605897b4211ad6e3e","nonce":"HMOD0L","pubkey":"EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443","rsakv":"1330428213","exectime":0})
        data = json.loads(urllib2.urlopen(url).read()[35:-1])
        # 获取有用信息，将与加密后密码一同post
        servertime, nonce, pubkey, rsakv = str(data['servertime']), data['nonce'], data['pubkey'], data['rsakv']
        key = rsa.PublicKey(int(pubkey,16), 65537)
        sp = rsa.encrypt(str(servertime) + '\t' + str(nonce) + '\n' + str(self.pw), key)
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
        #e.g location.replace("http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&ssosavestate=1394872359&ticket=ST-MjY0NjgwODY3MQ==-1392280359-gz-C29D9682D3DE6B9174BA3A502294B24A&retcode=0");
        # 已经成功一半，还要访问几个页面。
        req = urllib2.Request(re.search('location\.replace\("(.*)"\);', o.read()).group(1))
        o = self.opener.open(req)
        if "\u4e3a\u4e86\u60a8\u7684\u5e10\u53f7\u5b89\u5168\uff0c\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801" in o.read():
            raise Exception("为了您的帐号安全，请输入验证码")
        #e.g parent.sinaSSOController.feedBackUrlCallBack({"result":true,"userinfo":{"uniqueid":"2646808671","userid":null,"displayname":"\u6821\u56ed\u7ecf\u6d4e\u8d44\u8baf\u54c8\u54c8","userdomain":"?wvr=5&lf=reg"},"redirect":"http:\/\/weibo.com\/guide\/welcome"});
        # 成功
        return o.headers.status # , o.read()

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
    h = wb.urlopen('http://weibo.com/p/1005051716235922/weibo?profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1').read()
    id = re.search('version=mini&qid=heart&mid=([^&]*)&loc=profile', h).group(1)
    print id

