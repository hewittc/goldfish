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

class MemViewError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class MemViewReader(object):

    def __init__(self):
        global c_ptrace
        global c_waitpid

        libc_path = ctypes.util.find_library('c')
        if not libc_path:
            raise MemViewError('can not load libc')
        libc = ctypes.cdll.LoadLibrary(libc_path)

        c_ptrace = libc.ptrace
        c_ptrace.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]

        c_waitpid = libc.waitpid
        c_waitpid.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]

    def ptrace_scope_status(self):
        perm = -1
        msg = 'missing ptrace_scope'
        ptrace_scope = '/proc/sys/kernel/yama/ptrace_scope'

        if os.path.isfile(ptrace_scope) and os.access(ptrace_scope, os.R_OK):
            with open(ptrace_scope) as ptrace_scope:
                perm = int(ptrace_scope.readline())
                if perm is 0:
                    msg = 'classic ptrace permissions'
                elif perm is 1:
                    msg = 'restricted ptrace'
                elif perm is 2:
                    msg = 'admin-only attach'
                elif perm is 3:
                    msg = 'no attach'

        return (perm, msg)

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

    def get_stat_state(self, abbr):
        state = 'Unknown'
        if abbr in ('R', 'S', 'D', 'Z', 'T', 'W'):
            if abbr is 'R':
                state = 'Running'
            elif abbr is 'S':
                state = 'Sleeping'
            elif abbr is 'D':
                state = 'Disk Sleeping'
            elif abbr is 'Z':
                state = 'Zombie'
            elif abbr is 'T':
                state = 'Traced / Stopped'
            elif abbr is 'W':
                state = 'Paging'

        return state
                
    def _extract_stat(self, line):
        stat = re.match(r'(\d+)\s\((.+)\)\s([RSDZTW])\s(\d+)\s(\d+)\s(\d+)', line)
        pid = int(stat.group(1))
        comm = stat.group(2)
        state = self.get_stat_state(stat.group(3))
        ppid = int(stat.group(4))
        pgrp = int(stat.group(5))
        session = int(stat.group(6))

        return { 'pid': pid, 'comm': comm, 'state': state, 'ppid': ppid, 'pgrp': pgrp, 'session': session }

    def read_proc(self):
        return [ int(pid) for pid in os.listdir('/proc') if pid.isdigit() ]

    def read_proc_stat(self, pid):
        proc_stat = '/proc/{pid}/stat'.format(pid=pid)
        stat = None
        
        if os.path.isfile(proc_stat) and os.access(proc_stat, os.R_OK):
            with open(proc_stat, 'r') as fd:
                stat = self._extract_stat(fd.readline())
        else:
            stat = { 'pid': pid, 'comm': None, 'state': None, 'ppid': None, 'pgrp': None, 'session': None }

        return stat

    def read_proc_stat_all(self):
        return [ self.read_proc_stat(pid) for pid in self.read_proc() ]

    def read_proc_maps(self, pid):
        proc_maps = '/proc/{pid}/maps'.format(pid=pid)
        maps = None

        if not os.path.isfile(proc_maps) or not os.access(proc_maps, os.R_OK):
            raise MemViewError('can not read memory mapping for process \'{pid}\''.format(pid=pid))

        with open(proc_maps, 'r') as fd:
            maps = map(self._extract_maps, fd.readlines())

        return maps

    def read_proc_mem(self, pid):
        proc_mem = '/proc/{pid}/mem'.format(pid=pid)
        proc_maps = self.read_proc_maps()
        ranges = []

        if not os.path.isfile(proc_mem) or not os.access(proc_mem, os.R_OK):
            raise MemViewError('can not read memory for process \'{pid}\''.format(pid=pid))

        with open(proc_mem, 'rb') as fd:
            for proc_map in proc_maps:
                if proc_map['perms'][0] is 'r':
                    try:
                        fd.seek(proc_map['start'], 0)
                        proc_map['data'] = fd.read(proc_map['end'] - proc_map['start'])
                    except (OSError, ValueError) as err:
                        pass
                ranges.append(proc_map)

        return ranges

    def dump_mem(self):
        ptrace(PTRACE_ATTACH, pid, NULL, NULL)
        waitpid(pid, NULL, 0)
        processes = self.read_proc_mem()
        ptrace(PTRACE_DETACH, pid, NULL, NULL)

        for maps in processes:
            print('{start}-{end} [{perms}] {offset} {dev} {inode} {pathname}'.format(
                start=hex(maps['start']), 
                end=hex(maps['end']), 
                perms=maps['perms'],
                offset=hex(maps['offset']),
                dev=maps['dev'],
                inode=maps['inode'],
                pathname=maps['pathname']))

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
