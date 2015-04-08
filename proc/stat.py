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

class ProcStat(object):

    def __init__(self, pid):
        self.pid = pid

    def decode_state(self):
        result = 'Unknown'
        if self.state in ('R', 'S', 'D', 'Z', 'T', 'W'):
            if self.state is 'R':
                result = 'Running'
            elif self.state is 'S':
                result = 'Sleeping'
            elif self.state is 'D':
                result = 'Disk Sleeping'
            elif self.state is 'Z':
                result = 'Zombie'
            elif self.state is 'T':
                result = 'Traced / Stopped'
            elif self.state is 'W':
                result = 'Paging'

        return result


class ProcStatReader(object):

    def __init__(self):
        pass

    def get_pids(self):
        return ( int(pid) for pid in os.listdir('/proc') if pid.isdigit() )

    def decode_proc_stat(self, line):
        stat = re.match(r'(\d+)\s\((.+)\)\s([RSDZTW])\s(\d+)\s(\d+)\s(\d+)', line)
        result = dict()

        result['pid'] = int(stat.group(1))
        result['comm'] = stat.group(2)
        result['state'] = stat.group(3)
        result['ppid'] = int(stat.group(4))
        result['pgrp'] = int(stat.group(5))
        result['session'] = int(stat.group(6))

        return result

    def read_proc_stat(self, pid):
        proc_stat = '/proc/{pid}/stat'.format(pid=pid)
        result = ProcStat(pid)

        if os.path.isfile(proc_stat) and os.access(proc_stat, os.R_OK):
            with open(proc_stat, 'r') as fd:
                line = fd.readlines()[0]
                decoded = self.decode_proc_stat(line)
                for key in decoded:
                    setattr(result, key, decoded[key])

        return result

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
