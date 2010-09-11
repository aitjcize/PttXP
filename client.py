# client.py
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

import telnetlib
import time

class PttXPTelnetClient:
    def __init__(self):
        self.telnet = telnetlib.Telnet()

    def check_encode(self, text):
        try:
            text.decode('big5')
        except UnicodeDecodeError:
            return text.decode('utf8').encode('big5')
        else:
            return text

    def login(self, user, passwd):
        self.telnet.open('ptt.cc')
        print 'Logging in as %s ...' % user
        self.write('%s\r%s\r' % (user, passwd))
        data = self.telnet.read_until('[Y/n]')
        # Do not delete other login
        if data.endswith('[Y/n]'):
            self.write('n\r')
            time.sleep(3)
        self.key_enter()
        self.key_enter()

    def logout(self):
        print 'Logout'
        # TODO: find a better way
        for i in range(20):
            self.key_left()
        self.key_right()
        self.write('y\r')
        self.telnet.close()

    def key_enter(self):
        self.write('\r')
        self.output()

    def key_up(self):
        self.write('\033[A')
        self.output()

    def key_down(self):
        self.write('\033[B')
        self.output()

    def key_left(self):
        self.write('\033[D')
        self.output()

    def key_right(self):
        self.write('\033[C')
        self.output()

    def key_control(self, key):
        self.write(chr(ord(key) - ord('a') + 1))
        self.output()

    def key_pageup(self):
        self.write('\033[5~')
        self.output()

    def key_pagedown(self):
        self.write('\033[6~')
        self.output()

    def key_home(self):
        self.write('\033OH')
        self.output()

    def key_end(self):
        self.write('\033OF')
        self.output()

    def post(self, title, filename):
        print 'Posting %s ...' % title
        self.key_end()
        self.key_end()
        self.key_control('p')
        self.key_enter()
        self.write('%s\r' % self.check_encode(title))
        self.write_content_from_file(filename)
        print 'back'
        self.key_control('x')
        self.write('s\r')
        self.write('0\r')
    
    def write(self, data):
        self.telnet.write(data)
        self.output()

    def write_content_from_file(self, name):
        print 'writting from file %s ...' % name
        f = open(name, 'r')
        data = f.read().replace('\x1b', '\025')
        self.write(data)
        f.close()

    def go_board(self, board):
        print 'In board: %s' % board
        for i in range(5):
            self.key_left()
        self.write('s%s\r' % board)
        self.output()

    def output(self):
        data = self.telnet.read_very_eager()
        print data
        return data
