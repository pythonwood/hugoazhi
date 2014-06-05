firecookie导出的cookies.txt处理：
=================================

* :s/undefined\t//g

* 以下面四句开头:: 

    # Netscape HTTP Cookie File
    # http://curl.haxx.se/rfc/cookie_spec.html
    # This is a generated file!  Do not edit.
    (blank line)


Python中使用cookielib的FileCookieJar去save()，结果出错：NotImplementedError
================================================================================

默认的是FileCookieJar没有实现save函数。

而MozillaCookieJar或LWPCookieJar都已经实现了。

www.crifan.com/python_cookiejar_filecookiejar_save_error_notimplementederror/


从headers提取的，成功的cookies
=================================

源码::

    UOR=lyonna.me,widget.weibo.com,login.sina.com.cn; SINAGLOBAL=4510907964904.569.1400069195784;...

字典：用于request.get('http://weibo.com', cookies=cookies_dict)成功::

    # cookies_from_headers = dict(i.split('=') for i in cookie_raw.split(';')) # 制造方法

    {' ALF': '1433147993',
    ' Apache': '4942430828606.872.1401585724287',
    ' SINAGLOBAL': '4510907964904.569.1400069195784',
    ' SSOLoginState': '1401611994',
    ' SUB': 'Aaoqn%2Bo4nrDc5LARVzKmSXFBiJltfgrUwRBFA0ugO86%2BNF5SjvccnIz%2Bd22gHfYRApKEa8vrHYyl2yy4XIKPoSXJwPDQu8ysNsCUyrnfnfnQuZrtUARwH47BLLPS9015GdUUvBiEWjDNSJGkucqCZW0%3D',
    ' SUBP': '002A2c-gVlwEm1uAWxfgXELuuu1xVxBxA7phgc1UHDv39FD4Xz-6p0HuHY-u_1%3D',
    ' SUE': 'es%3D3db7d59178491b37185ccfffb1b64dc8%26ev%3Dv1%26es2%3D293278eab803b9addb3cd020ebb7ca4e%26rs0%3Djb%252BYBMk%252B%252BxrLBhgvcs06jNWt42t6fhJ3bndL5mHEhKSt0l3p2NeJQhWl40ZLqFNFhJdV4Np%252BsbfPYmzp1Ea%252FGA%252BpU0Kh2HqpDVExh7G2YGwnunexvvaiyJSKBrysx4PNZQHm5fcnVjKVuVejRqmwd89dsn%252B98I%252FLjYBFPGz74Wc%253D%26rv%3D0',
    ' SUP': 'cv%3D1%26bt%3D1401611994%26et%3D1401698394%26d%3Dc909%26i%3D093f%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D19%26st%3D0%26uid%3D2646808671%26name%3D13750022544%2540163.com%26nick%3D%25E6%25A0%25A1%25E5%259B%25AD%25E7%25BB%258F%25E6%25B5%258E%25E8%25B5%2584%25E8%25AE%25AF%25E5%2593%2588%25E5%2593%2588%26fmp%3D%26lcp%3D',
    ' SUS': 'SID-2646808671-1401611994-GZ-uk6ws-df94f954ac98fb2d95c59b515819093f',
    ' ULV': '1401585724309:43:2:2:4942430828606.872.1401585724287:1401562933438',
    ' YF-Page-G0': 'e3ff5d70990110a1418af5c145dfe402',
    ' YF-Ugrow-G0': 'cd9e8fbbed8e8c42cab38a5786ea18b7',
    ' YF-V5-G0': '694581d81c495bd4b6d62b3ba4f9f1c8',
    ' _s_tentry': 'login.sina.com.cn',
    ' login_sid_t': '422875222386a0e6daba6f0373c611c4',
    ' myuid': '2170514824',
    ' un': '13750022544@163.com',
    ' wvr': '5',
    'UOR': 'lyonna.me,widget.weibo.com,login.sina.com.cn'}
    
    (' ALF',' Apache',' SINAGLOBAL',' SSOLoginState',' SUB',' SUBP',' SUE',' SUP',' SUS',' ULV',' YF-Page-G0',' YF-Ugrow-G0',' YF-V5-G0',' _s_tentry',' login_sid_t',' myuid',' un',' wvr','UOR')



评论search，每三个一组，首页包含3次。
(pre_page=0,page=1,pagebar=0),(pre_page=1,page=1,pagebar=0),(pre_page=1,page=1,pagebar=1)
http://weibo.com/p/aj/mblog/mbloglist?_wv=5&domain=100505&pre_page=0&page=1&max_id=3708816657175473&end_id=3716789328888062&count=15&pagebar=0&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__24&id=1005051716235922&script_uri=/p/1005051716235922/weibo&feed_type=0&profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1&__rnd=1401772208635
http://weibo.com/p/aj/mblog/mbloglist?_wv=5&domain=100505&pre_page=1&page=1&max_id=3708816657175473&end_id=3716789328888062&count=15&pagebar=0&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__24&id=1005051716235922&script_uri=/p/1005051716235922/weibo&feed_type=0&profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1&__rnd=1401772208635
http://weibo.com/p/aj/mblog/mbloglist?_wv=5&domain=100505&pre_page=1&page=1&max_id=3708816657175473&end_id=3716789328888062&count=15&pagebar=1&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__24&id=1005051716235922&script_uri=/p/1005051716235922/weibo&feed_type=0&profile_ftype=1&key_word=%E5%BA%8A%E5%89%8D%E6%98%8E%E6%9C%88%E5%85%89&is_search=1&__rnd=1401772208635
