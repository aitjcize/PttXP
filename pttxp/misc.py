# misc.py
#
# Copyright (C) 2010 -  Wei-Ning Huang (AZ) <aitjcize@gmail.com>
# All Rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from os.path import abspath, dirname
import sys
import gettext, platform

# Installation information
LIB_PATH = '/usr/lib/pttxp'
SHARE_PATH = '/usr/share/pttxp'

# Operating system
running_os = platform.system()

# Program Information
program_name = 'PttXP'
program_version = '0.1.5.2'

program_logo = SHARE_PATH + '/pttxp.png'
ui_file = SHARE_PATH + '/pttxp.glade'

# If lanuch from source directory
if not sys.argv[0].startswith('/usr/bin'):
    prefix = dirname(abspath(sys.argv[0]))
    program_logo = prefix + '/../data/pttxp.png'
    ui_file = prefix + '/../data/pttxp.glade'

# For py2exe packaging
if running_os == 'Windows':
    program_logo = 'pttxp.png'
    ui_file = 'pttxp.glade'
