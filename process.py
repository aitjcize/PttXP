# process.py
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

import re
import time

from client import PttXPTelnetClient

class PttXPScriptRunner:
    def __init__(self):
        self.client = PttXPTelnetClient()
        self.cmds = {}
        self.cmds['^#login ([^,]*),(.*)'] = self.client.login
        self.cmds['^#logout'] = self.client.logout
        self.cmds['^#enter'] = self.client.key_enter
        self.cmds['^#up'] = self.client.key_up
        self.cmds['^#down'] = self.client.key_down
        self.cmds['^#left'] = self.client.key_left
        self.cmds['^#right'] = self.client.key_right
        self.cmds['^#pageup'] = self.client.key_pageup
        self.cmds['^#pagedown'] = self.client.key_pagedown
        self.cmds['^#home'] = self.client.key_home
        self.cmds['^#end'] = self.client.key_end
        self.cmds['^#ctrl-([a-z])'] = self.client.key_control
        self.cmds['^#goboard (.*)'] = self.client.go_board
        self.cmds['^#postfile ([^,]*),(.*)'] = self.client.post
        self.cmds['^#fromfile (.*)'] = self.client.write_content_from_file

    def run(self, script):
        controls = script.split('\n')
        for term in controls:
            time.sleep(0.3)
            for key in self.cmds:
                got = re.findall(key, term)
                var = key.count('(')
                if got:
                    if var == 0:
                        self.cmds[key]()
                        break;
                    elif var == 1:
                        self.cmds[key](got[0])
                        break;
                    elif var == 2:
                        self.cmds[key](got[0][0], got[0][1])
                        break;
            else:
                self.client.write(term)
