#!/usr/bin/env python
#-*- coding: utf-8 -*-

from process import PttXPScriptRunner
import time

b = PttXPScriptRunner()
f = open('list.txt', 'r')
boards = f.readlines()
f.close()

f = open('result.txt', 'w+')

count = 0

for x in boards:
    if count == 0:
        b.run('#login azhuang,ptfs2081127')

    b.run('#goboard %s' % x)
    f.write(x)
    b.run('#postfile 台大國術社  體驗課9/13 9/15 在舊體後,post.txt')
    count += 1

    if count == 4:
        count = 0
        b.run('#logout')
        time.sleep(3)
