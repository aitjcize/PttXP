# client.py
#-*- coding: utf-8 -*-
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

import platform
import telnetlib
import time
import re
import sys

class PttXPLoginError(Exception):
    pass

class PttXPLoginFatal(Exception):
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
        if self.connected:
            self.telnet.close()
            self.connected = False
            self.loggedin = False
        try:
            self.telnet.open(host)
        except:
            self.print_message('(EE) Invalid host - %s.' % host)
            raise PttXPLoginFatal

        self.connected = True

    def login(self, host, user, passwd):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.loggedin = False
        try:
            self.telnet.open(host)
        except:
            self.print_message('(EE) Invalid host - %s.' % host)
            raise PttXPLoginFatal

        self.print_message('(II) Logging in as %s ...' % user)
        word = self.telnet.read_until(self.tobig5('註冊'), 1)

        self.telnet.write('%s\r%s\r' % (user, passwd))

        login_status = self.telnet.read_until('[Y/n]', 3)[-320:]

        # Do not delete other login
        if self.tobig5('刪除其他重複登入的連線嗎？') in login_status:
            self.telnet.write('n\r')
            login_status = self.telnet.read_until(
                    self.tobig5('請按任意鍵繼續'))[-320:]
            self.print_message('(WW) Multiple login detected, continuing.')

        if self.tobig5('頻繁登入') in login_status:
            self.telnet.write('\r')
            login_status = self.telnet.read_until('Dummy', 5)[-320:]
            self.print_message('(WW) PTT Warning: Login too frequently.')

        if self.tobig5('登入太頻繁') in login_status:
            self.print_message('(EE) PTT Error: Login too frequently, please '
                    'retry later or change the account.')
            raise PttXPLoginFatal

        if not self.tobig5('請按任意鍵繼續') in login_status:
            self.loggedin = False
            self.print_message('(EE) Login failed.')
            raise PttXPLoginError

        self.key_enter('再見')

        # Skip prompt for saving unfinished post
        data = self.telnet.read_until('[S]', 3)
        if '[S]' in data:
            self.write('q\r', '再見')
        #else:
        #    self.key_enter()

        self.loggedin = True


    def logout(self):
        self.print_message('(II) Logout')
        # TODO: find a better way
        '''
        try:
            for i in range(20):
                self.telnet.write('\033[D')
                self.output()
            self.key_right()
            self.telnet.write('y\r')
            self.telnet.close()
        except: pass
        '''
        # phoenix104104: not sure whether direct close telnet is a better way (2014/01/20)
        self.telnet.close()
        self.loggedin = False

    def key_enter(self, word=0):
        self.write('\r', word)

    def key_up(self, word=0):
        self.write('\033[A', word)

    def key_down(self, word=0):
        self.write('\033[B', word)

    def key_left(self, word=0):
        self.write('\033[D', word)

    def key_right(self, word=0):
        self.write('\033[C', word)

    def key_control(self, key, word=0):
        self.write(chr(ord(key) - ord('a') + 1), word)

    def key_pageup(self, word=0):
        self.write('\033[5~', word)

    def key_pagedown(self, word=0):
        self.write('\033[6~', word)

    def key_home(self, word=0):
        self.write('\033OH', word)

    def key_end(self, word=0):
        self.write('\033OF', word)

    def postfile(self, title, filename):
        self.print_message('(II) Posting %s ...' % title)
        # press end to prevent pressing ctrl-p in the welcome page
        self.key_end('繼續')
        self.key_end('進板畫面')
        self.key_control('p', '不選')
        self.key_enter('標題：')
        self.write('%s\r' % self.check_encode(title))
        self.write_content_from_file(filename)
        self.key_control('x', '檔案嗎？')
        self.write('s\r')
        self.write('0\r')

    def delete_header(self, board):
        self.print_message('(II) Deleting header ...')
        self.go_board(board, True)
        self.key_end()
        self.key_end()
        self.write('a')
        self.write('%s' % self.user)
        self.key_enter()
        self.key_end()
        self.key_end()
        self.key_left()
        self.write('E')
        self.key_control('y')
        self.key_control('y')
        self.key_control('y')
        self.key_control('y')
        self.key_control('x')
        self.write('s\r')
        self.key_enter()
        self.key_enter()

    def crosspost(self, limit, delete_header, boardlist, title, filename):
        self.print_message('(II) Start')
        if not self.loggedin:
            self.print_message('(EE) Please login first!')
            exit(1)

        limit = int(limit)
        # logout first to prevent crossing the cp_limit
        self.logout()
        count = 0
        if 'Windows' == platform.system():
            boardlist = boardlist.decode('utf8').encode('big5')

        f = open(boardlist, 'r')
        boards = f.readlines()
        f.close()

        for b in boards:
            b = b.strip()
            if self.stop:
                self.logout()
                self.print_message('(EE) Interrupted\n')
                return

            if count == 0:
                for i in range(5):
                    try:
                        self.login(self.host, self.user, self.passwd)
                    except PttXPLoginError:
                        if i == 4:
                            self.print_message('(II) Abort\n')
                            return
                        else:
                            self.print_message('(II) Retring ...')
                            self.logout()
                    else:
                        break

            self.go_board(b)
            self.postfile(title, filename)
            if 'True' == delete_header:
                self.delete_header(b)
            count += 1
            if count == limit -1:
                count = 0
                self.logout()
                time.sleep(1)

        self.logout()
        self.print_message('(II) All Finished\n')


    def write(self, data, word=0):

        if 0 == len(data): return
        try:
            self.telnet.write(data)
            #self.output()

            if word != 0 :
                getStr = self.telnet.read_until(self.tobig5(word), 0.1)
                #print "Expected word: %s" %word
                #if self.tobig5(word) in getStr:
                #    print "Find %s" %word
            else:
                self.output()
                time.sleep(0.1)

        except AttributeError:
            self.print_message('(EE) Write error')

    def write_content_from_file(self, name):
        self.print_message('(II) Writting from file %s ...' % name)
        if 'Windows' == platform.system():
            name = self.check_encode(name)

        f = open(name, 'r')
        data = self.check_encode(f.read())

        # replace \x1b with \025 to provide ANSI color output
        data = data.replace('\x1b', '\025')

        # windows version of telnetlib won't send \r
        if 'Windows' == platform.system():
            data = data.replace('\n', '\n\r')

        self.write(data)
        f.close()

    def go_board(self, board, mute=False):
        #for i in range(10):
        #    self.key_left()
        self.write('s', '搜尋')
        self.write('%s\r' % board)

        if not mute:
            self.print_message('\n(II) In board: %s' % board)


    def print_message(self, msg):
        print msg

    def output(self):
        data = self.telnet.read_very_eager()
        return data

    def tobig5(self, str):
        return str.decode('utf8').encode('big5')

    def toutf8(self, str):
        return str.decode('big5').encode('utf8')

    def filterWord(self, word):
        word = re.sub(r'\033\[.*?m', '', word)
        word = word.decode('big5', 'ignore').encode('utf8')
        return word

    def dump(self, fileName, str):
        f = open(fileName, 'w')
        f.write(str)
        f.close()
        print 'dump txt file: %s' %fileName
