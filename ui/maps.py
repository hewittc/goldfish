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

from gi.repository import Gtk

class GUIMapsWindow(Gtk.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(title='Memory Maps')
        self.set_size_request(900, 400)

        self.mmap_treeview_scroller = self.create_mmap_list()

        vbox = Gtk.VBox()
        vbox.pack_start(self.mmap_treeview_scroller, expand=True, fill=True, padding=0)
        self.add(vbox)

        self.show_all()

    def create_mmap_list(self):
        self.mmap_liststore = Gtk.ListStore(str, str, str, str, str, str, str)

        mmap_liststore_sorted = Gtk.TreeModelSort(model=self.mmap_liststore)
        mmap_liststore_sorted.set_sort_column_id(0, Gtk.SortType.DESCENDING)

        mmap_treeview = Gtk.TreeView(model=mmap_liststore_sorted)

        text_left_aligned = Gtk.CellRendererText(xalign=0)
        text_right_aligned = Gtk.CellRendererText(xalign=1)

        column_address_start = Gtk.TreeViewColumn('Address Start', text_right_aligned, text=0)
        column_address_start.set_sort_column_id(0)
        mmap_treeview.append_column(column_address_start)

        column_address_end = Gtk.TreeViewColumn('Address End', text_right_aligned, text=1)
        column_address_end.set_sort_column_id(1)
        mmap_treeview.append_column(column_address_end)

        column_perms = Gtk.TreeViewColumn('Permissions', text_right_aligned, text=2)
        column_perms.set_sort_column_id(2)
        mmap_treeview.append_column(column_perms)

        column_offset = Gtk.TreeViewColumn('Offset', text_right_aligned, text=3)
        column_offset.set_sort_column_id(3)
        mmap_treeview.append_column(column_offset)

        column_device = Gtk.TreeViewColumn('Device', text_right_aligned, text=4)
        column_device.set_sort_column_id(4)
        mmap_treeview.append_column(column_device)

        column_inode = Gtk.TreeViewColumn('Inode', text_right_aligned, text=5)
        column_inode.set_sort_column_id(5)
        mmap_treeview.append_column(column_inode)

        column_pathname = Gtk.TreeViewColumn('Path', text_right_aligned, text=6)
        column_pathname.set_sort_column_id(6)
        mmap_treeview.append_column(column_pathname)

        mmap_treeview_scroller = Gtk.ScrolledWindow()
        mmap_treeview_scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        mmap_treeview_scroller.add(mmap_treeview)

        return mmap_treeview_scroller

    def update_mmap_list(self, maps):
        self.mmap_liststore.clear()
        for mmap in mmaps:
            self.mmap_liststore.append([mmap.address_start, mmap.address_end, mmap.perms, mmap.offset, mmap.device, mmap.inode, mmap.pathname])

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
