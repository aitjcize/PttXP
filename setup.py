#!/usr/bin/env python

from distutils.core import setup
from DistUtilsExtra.command import *

_data_files = [
	('share/applications', ['data/pttxp.desktop']),
	('share/pixmaps', ['data/pttxp.png']),
	('share/pttxp/', ['data/pttxp.png']),
	('share/pttxp/', ['data/pttxp.glade']),
	]

files = ["doc/README",
         "doc/AUTHORS",
         "doc/COPYING",
         "doc/Changlog"]

setup(
	name = 'pttxp',
	version = '0.1.0',
	description = 'Ptt Posting/Scripting Utility',
	author = 'Wei-Ning Huang (AZ)',
	author_email = 'aitjcize@gmail.com',
        url = 'http://github.com/Aitjcize/pttxp',
	license = 'GPL',
    	packages = ['pttxp'],
	package_data = {'pttxp' : files },
	scripts = ['bin/pttxp'],
	data_files = _data_files
)
