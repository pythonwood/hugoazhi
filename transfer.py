#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
import os
from bs4 import BeautifulSoup
def transfer(filepath):
    print filepath
    items = []
    nav_items = []
    filename = filepath.split('/')[-1]
    title = list(filename[:-5])
    title[10]=' '
    title[13]=':'
    title = ''.join(title).decode('utf-8')
    with open(filepath) as f:
        bs = BeautifulSoup(f.read())
    for i,li in enumerate(bs.find_all('li')):
        i += 1
        li.a.unwrap()
        del li.img['usercard']
        del li.img['alt']
        del li.a['usercard']
        del li.a['title']
        li.insert(2, '#%s'%i)
        if i%100 == 0:
            li['id'] = "t%s"%i
            nav_items.append(u'<li class=""><a href="#t%s">%s</a></li>' % (i,i/100))
        items.append(li.prettify())
    h = html_tpl % (title, u'\n'.join(nav_items), title, u'\n'.join(items))
    with open(filepath, 'w') as f:
        f.write(h.encode('utf-8'))
    return len(h)

def main():
    # dirname = '/media/E/loveq-weibo/test/'
    dirname = '/media/E/loveq-weibo/comment/'
    for filename in os.listdir(dirname):
        filepath = os.path.join(dirname, filename)
        transfer(filepath)


if __name__ == "__main__":
    ''''''
    # main()

