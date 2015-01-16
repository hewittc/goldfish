#
# Copyright (C) 2015 Christopher Hewitt
#
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

from gi.repository import Gdk, Gtk

from ui_maps_list import MemViewUIMapsList

class MemViewUIProcListWindow(Gtk.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(title='Goldfish (Process List)')
        self.set_size_request(600, 600)
        self.connect('destroy', Gtk.main_quit)

        self.process_liststore = Gtk.ListStore(int, str, str, int, int, int)
        self.renderer_text = Gtk.CellRendererText()

        self.vbox = Gtk.VBox()

        self.process_treeview_scroller = Gtk.ScrolledWindow()
        self.process_treeview_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.process_treeview = Gtk.TreeView(model=self.process_liststore)

        self.column_pid_text = Gtk.TreeViewColumn('PID', self.renderer_text, text=0)
        self.column_filename_text = Gtk.TreeViewColumn('Filename', self.renderer_text, text=1)
        self.column_state_text = Gtk.TreeViewColumn('State', self.renderer_text, text=2)
        self.column_ppid_text = Gtk.TreeViewColumn('Parent PID', self.renderer_text, text=3)
        self.column_pgrp_text = Gtk.TreeViewColumn('Process GID', self.renderer_text, text=4)
        self.column_session_text = Gtk.TreeViewColumn('Session ID', self.renderer_text, text=5)


        self.process_treeview.append_column(self.column_pid_text)
        self.process_treeview.append_column(self.column_filename_text)
        self.process_treeview.append_column(self.column_state_text)
        self.process_treeview.append_column(self.column_ppid_text)
        self.process_treeview.append_column(self.column_pgrp_text)
        self.process_treeview.append_column(self.column_session_text)


        self.process_treeview_scroller.add(self.process_treeview)

        self.ptrace_status_label = Gtk.Label('None', xalign=1)

        self.vbox.pack_start(self.process_treeview_scroller, True, True, 0)
        self.vbox.pack_start(self.ptrace_status_label, False, True, 0)

        self.add(self.vbox)

        self.show_all()

    def update_ptrace_label(self, msg):
        self.ptrace_status_label.set_text('Process trace restrictions: {msg}'.format(msg=msg))

    def update_process_liststore(self, processes):
        self.process_liststore.clear()
        for process in processes:
            self.process_liststore.append([process['pid'], process['comm'], process['state'], process['ppid'], process['pgrp'], process['session']])

    def run(self):
        Gtk.main()

if __name__ == '__main__':
    MemViewUIWindow()

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
