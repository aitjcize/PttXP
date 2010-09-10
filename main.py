#!/usr/bin/env python

from process import BBSXPScriptRunner
b = BBSXPScriptRunner()
b.run(open('test.script', 'r').read())
