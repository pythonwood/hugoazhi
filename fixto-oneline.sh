#!/bin/bash
#coding: utf-8
for file in /media/E/loveq/weibo/*;
do
    # echo $file;
    # 现在使用来清空holdspace，/<li>/!H;/<li>/h; D指令总是“sed: couldn't re-allocate memory”
    sed -i '/list-unstyled/,/<\/ul>/{/<li>/,/<\/li>/{/<li>/!H;/<li>/h;/<\/li>/{g;s/\n//g};/<\/li>/!d}}' $file;
done;

