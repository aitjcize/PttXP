#!/usr/bin/env python

import gtk
import os.path

from client import PttXPTelnetClient, PttXPLoginError
from runner import PttXPScriptRunner, HELPTEXT
from misc import *

class PttXPGuiTelnetClient(PttXPTelnetClient):
    def __init__(self, textview):
        PttXPTelnetClient.__init__(self)
        self.textview = textview
        self.textbuffer = textview.get_buffer()

    def print_message(self, message):
        print message
        end = self.textbuffer.get_end_iter()
        self.textbuffer.insert(end, '%s\n' %message)
        self.textview.scroll_to_mark(self.textbuffer.get_insert(),
                                     0.25, False, 0.0, 0.0)
        while gtk.events_pending(): gtk.main_iteration()

class PttXPGui:
    def __init__(self):
        # GUI related
        self.builder = gtk.Builder()
        self.builder.add_from_file(ui_file)
        self.builder.connect_signals(self)
        self.mainwindow = self.builder.get_object('mainwindow')
        self.host = self.builder.get_object('host')
        self.user = self.builder.get_object('user')
        self.passwd = self.builder.get_object('passwd')
        self.boardlist = self.builder.get_object('boardlist')
        self.boardlist_button = self.builder.get_object('boardlist_button')
        self.limit = self.builder.get_object('limit')
        self.title = self.builder.get_object('title')
        self.content = self.builder.get_object('content')
        self.content_button = self.builder.get_object('content_button')
        self.post_start_button = self.builder.get_object('post_start_button')
        self.post_stop_button = self.builder.get_object('post_stop_button')
        self.post_message = self.builder.get_object('post_message')
        self.xdscript = self.builder.get_object('xdscript')
        self.run_start_button = self.builder.get_object('run_start_button')
        self.run_stop_button = self.builder.get_object('run_stop_button')
        self.run_message = self.builder.get_object('run_message')
        self.helpview = self.builder.get_object('helpview')
        self.aboutdialog = self.builder.get_object('aboutdialog')

        helpbuffer = self.helpview.get_buffer()
        helpbuffer.set_text(HELPTEXT)

        self.post_message_buffer = self.post_message.get_buffer()
        self.limit.set_value(5)

        self.post_client = PttXPGuiTelnetClient(self.post_message)
        self.script_client = PttXPGuiTelnetClient(self.run_message)
        self.script_runner = PttXPScriptRunner(self.script_client, True)

        gtk.window_set_default_icon_from_file(program_logo)
        self.mainwindow.set_title('%s %s' % (program_name, program_version))
        self.mainwindow.set_position(gtk.WIN_POS_CENTER)
        self.mainwindow.show_all()
        gtk.main()

    def gui_quit(self, evnet, user):
        gtk.main_quit()

    def post_print_message(self, message):
        self.post_client.print_message(message)

    def script_print_message(self, message):
        self.script_client.print_message(message)

    def on_post_start_button_clicked(self, widget):
        self.post_print_message('------------- Start -------------\n')
        host = self.host.get_text()
        user = self.user.get_text()
        passwd = self.passwd.get_text()
        boardlist = self.boardlist.get_text()
        limit = self.limit.get_value()
        title = self.title.get_text()
        content = self.content.get_text()

        if not (host and user and passwd and boardlist and title and content):
            self.post_print_message('Please fill all blanks!')
            return

        self.post_client.stop = False
        try:
            self.post_client.login(host, user, passwd)
        except PttXPLoginError:
            self.post_print_message('\n----------- Abort -----------\n')
            return
        self.post_client.crosspost(limit, boardlist, title, content)
        self.post_print_message('\n----------- All Finished -----------\n')

    def on_post_stop_button_clicked(self, widget):
        self.post_client.stop = True

    def on_content_button_clicked(self, widget):
        name = self.get_filename()
        if name:
            self.content.set_text(name)

    def on_boardlist_button_clicked(self, widget):
        name = self.get_filename()
        if name:
            self.boardlist.set_text(name)
    
    def on_run_start_button_clicked(self, widget):
        self.script_print_message('------------- Start -------------\n')
        self.script_runner.stop = False
        textbuffer = self.xdscript.get_buffer()
        start, end = textbuffer.get_bounds()
        script = textbuffer.get_text(start, end)
        self.script_runner.run(script)
        self.script_print_message('\n----------- All Finished -----------\n')

    def on_run_stop_button_clicked(self, widget):
        self.script_runner.stop = True

    def on_about_button_clicked(self, widget):
        about = gtk.AboutDialog()
        about.set_transient_for(self.mainwindow)
        about.set_position(gtk.WIN_POS_CENTER)
        about.set_name(program_name)
        about.set_version(program_version)
        about.set_comments('Ptt Posting/Scriting Utility')
        about.set_license('''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
''')
        about.set_copyright('Copyright 2010 Wei-Ning Huang (AZ)')
        about.set_website('http://berelent.blogspot.com/2010/09/pttxp-ptt.html')
        about.set_website_label('PttXP at GitHub')
        about.set_authors(['Wei-Ning Huang (AZ) <aitjcize@gmail.com>'])
        about.set_logo(gtk.gdk.pixbuf_new_from_file_at_size(program_logo,
            96, 96))
        about.connect('response', lambda x, y, z: about.destroy(), True)
        about.show_all()
 
    def get_filename(self):
        chooser = gtk.FileChooserDialog("Browse", self.mainwindow,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        chooser.set_current_folder(os.path.expanduser('~'))
        response = chooser.run()
        name = chooser.get_filename()
        chooser.destroy()

        if response == gtk.RESPONSE_CANCEL:
            return None
        else:
            return name

if __name__ == '__main__':
    PttXPGui()
