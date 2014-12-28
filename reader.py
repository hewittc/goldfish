#
# Copyright (C) 2014 Christopher Hewitt
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

NULL          = 0
PTRACE_ATTACH = 16
PTRACE_DETACH = 17

def ptrace(request, pid, addr, data):
    ''' long ptrace(enum __ptrace_request request, pid_t pid, void *addr, void *data); '''
    global c_ptrace

    c_request  = ctypes.c_int(request)
    c_pid      = ctypes.c_int(pid)
    c_addr     = ctypes.c_void_p(addr)
    c_data     = ctypes.c_void_p(addr)

    return c_ptrace(c_request, c_pid, c_addr, c_data)

def waitpid(pid, stat_loc, options):
    ''' pid_t waitpid(pid_t pid, int *stat_loc, int options); '''
    global c_waitpid

    c_pid      = ctypes.c_int(pid)
    c_stat_loc = ctypes.c_void_p(stat_loc)
    c_options  = ctypes.c_int(options)

    return c_waitpid(c_pid, c_stat_loc, c_options)

class MemViewReader(object):

    def __init__(self, pid):
        global c_ptrace
        global c_waitpid

        self.pid = pid
        self.proc_maps = '/proc/{pid}/maps'.format(pid=self.pid)
        self.proc_mem = '/proc/{pid}/mem'.format(pid=self.pid)

        if not os.path.isfile(self.proc_maps) or not os.access(self.proc_maps, os.R_OK):
            print('error: can not read memory mapping for process {pid}'.format(pid=self.pid))
            sys.exit(-1)

        if not os.path.isfile(self.proc_mem) or not os.access(self.proc_mem, os.R_OK):
            print('error: can not read memory for process {pid}'.format(pid=self.pid))
            sys.exit(-1)

        libc_path = ctypes.util.find_library('c')
        libc = ctypes.cdll.LoadLibrary(libc_path)

        c_ptrace = libc.ptrace
        c_ptrace.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]

        c_waitpid = libc.waitpid
        c_waitpid.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]

    def _extract_range(self, line):
        mem_range = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r][-w][-x][sp])', line)
        start = int(mem_range.group(1), 16)
        end = int(mem_range.group(2), 16)
        privs = mem_range.group(3)
        data = None

        return { 'start': start, 'end': end, 'privs': privs, 'data': data }

    def read_proc_maps(self):
        ranges = None

        with open(self.proc_maps, 'r') as fd:
            ranges = map(self._extract_range, fd.readlines())

        return ranges

    def read_proc_mem(self):
        ranges = []
        proc_maps = self.read_proc_maps()

        with open(self.proc_mem, 'rb') as fd:
            for proc_map in proc_maps:
                if proc_map['privs'][0] is 'r':
                    try:
                        fd.seek(proc_map['start'], 0)
                    except ValueError as err:
                        pass
                    try:
                        proc_map['data'] = fd.read(proc_map['end'] - proc_map['start'])
                    except OSError as err:
                        pass
                ranges.append(proc_map)

        return ranges

    def dump_mem(self):
        ptrace(PTRACE_ATTACH, self.pid, NULL, NULL)
        waitpid(self.pid, NULL, 0)
        ranges = self.read_proc_mem()
        ptrace(PTRACE_DETACH, self.pid, NULL, NULL)

        for mem_range in ranges:
            print('{start}-{end} [{privs}]'.format(
                start=hex(mem_range['start']), 
                end=hex(mem_range['end']), 
                privs=mem_range['privs']))

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
