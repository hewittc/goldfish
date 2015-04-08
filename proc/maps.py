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

import os
import re
import sys
import binascii
import ctypes
import ctypes.util

class ProcMaps(object):

    def __init__(self):
        pass

    def _extract_maps(self, line):
        maps = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+)\s+([-r][-w][-x][sp])\s+([0-9A-Fa-f]+)\s+([:0-9A-Fa-f]+)\s+([0-9A-Fa-f]+)\s+(.*)$', line)
        start = int(maps.group(1), 16)
        end = int(maps.group(2), 16)
        perms = maps.group(3)
        offset = int(maps.group(4), 16)
        dev = maps.group(5)
        inode = maps.group(6)
        pathname = maps.group(7)
        data = None

        return { 'start': start, 'end': end, 'perms': perms, 'offset': offset, 'dev': dev, 'inode': inode, 'pathname': pathname, 'data': data }

    def read_proc_maps(self, pid):
        proc_maps = '/proc/{pid}/maps'.format(pid=pid)
        maps = None

        if not os.path.isfile(proc_maps) or not os.access(proc_maps, os.R_OK):
            raise MemViewError('can not read memory mapping for process \'{pid}\''.format(pid=pid))

        with open(proc_maps, 'r') as fd:
            maps = map(self._extract_maps, fd.readlines())

        return maps

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
