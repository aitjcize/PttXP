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

class PttXPLoginError(Exception):
    pass

class PttXPTelnetClient:
    def __init__(self):
        self.telnet = telnetlib.Telnet()
        self.stop = False
        self.loggedin = False
        self.connected = False

    def check_encode(self, text):
        try:
            text.decode('big5')
        except UnicodeDecodeError:
            return text.decode('utf8').encode('big5')
        else:
            return text

    def connect(self, host):
        print 'here'
        if self.connected:
            self.telnet.close()
            self.connected = False
            self.loggedin = False
        self.telnet.open(host)
        self.connected = True

    def login(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.loggedin = False
        try:
            self.telnet.open(host)
        except socket.gaierror:
            self.print_message('Ivalid host.')
            return
        self.print_message('Logging in as %s ...' % user)
        self.output()
        self.telnet.write('%s\r%s\r' % (user, passwd))

        data = self.telnet.read_until('[Y/n]', 3)
        # Do not delete other login
        if '[Y/n]' in data:
            self.write('n\r')
            time.sleep(3)
        if 'guest' in data:
            self.loggedin = False
            self.print_message('Login failed.')
            raise PttXPLoginError
        self.key_enter()
        self.key_enter()
        self.loggedin = True

    def logout(self):
        self.print_message('Logout')
        # TODO: find a better way
        for i in range(20):
            self.telnet.write('\033[D')
            self.output()
        self.key_right()
        self.telnet.write('y\r')
        self.telnet.close()
        self.loggedin = False

    def key_enter(self):
        self.write('\r')

    def key_up(self):
        self.write('\033[A')

    def key_down(self):
        self.write('\033[B')

    def key_left(self):
        self.write('\033[D')

    def key_right(self):
        self.write('\033[C')

    def key_control(self, key):
        self.write(chr(ord(key) - ord('a') + 1))

    def key_pageup(self):
        self.write('\033[5~')

    def key_pagedown(self):
        self.write('\033[6~')

    def key_home(self):
        self.write('\033OH')

    def key_end(self):
        self.write('\033OF')

    def postfile(self, title, filename):
        self.print_message('Posting %s ...' % title)
        self.key_end()
        self.key_end()
        self.key_control('p')
        self.key_enter()
        self.write('%s\r' % self.check_encode(title))
        self.write_content_from_file(filename)
        self.key_control('x')
        self.write('s\r')
        self.write('0\r')

    def crosspost(self, limit, boardlist, title, filename):
        if not self.loggedin:
            self.print_message('Please login first!')
            exit(1)

        limit = int(limit)
        self.logout()
        count = 0
        f = open(boardlist, 'r')
        boards = f.readlines()
        f.close()

        for b in boards:
            if self.stop:
                self.logout()
                return
            if count == 0:
                self.login(self.host, self.user, self.passwd)
            self.go_board(b)
            self.postfile(title, filename)
            count += 1
            time.sleep(1)
            if count == limit -1:
                count = 0
                self.logout()
                time.sleep(2)
        self.logout()
    
    def write(self, data):
        try:
            self.telnet.write(data)
            self.output()
        except AttributeError:
            self.print_message("Write error")

    def write_content_from_file(self, name):
        self.print_message('Writting from file %s ...' % name)
        f = open(name, 'r')
        data = f.read().replace('\x1b', '\025')
        self.write(data)
        f.close()

    def go_board(self, board):
        self.print_message('In board: %s' % board)
        for i in range(5):
            self.key_left()
        self.write('s%s\r' % board)

    def print_message(self, msg):
        print msg

    def output(self):
        data = self.telnet.read_very_eager()
        return data
