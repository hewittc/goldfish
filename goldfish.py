#!/usr/bin/env python3

import sys

from reader import MemViewReader

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print('usage: {} <pid>'.format(sys.argv[0]))
        sys.exit(-1)

    pid = int(sys.argv[1])
    mvr = MemViewReader(pid)
    mvr.dump_mem()

# vim: autoindent tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
