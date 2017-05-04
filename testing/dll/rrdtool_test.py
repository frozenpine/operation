import ctypes
import time
import sys
from os import path
CUR_DIR = path.dirname(sys.argv[0])
sys.path.append(CUR_DIR)
import rrdtool
DLL_FILE = path.join(CUR_DIR, 'rrdtool.dll')
'''
if path.isfile(DLL_FILE):
    #rrdtool = ctypes.WinDLL(DLL_FILE)
    rrdtool = ctypes.CDLL(DLL_FILE)
'''

if __name__ == '__main__':
    start = int(time.mktime((2006, 1, 1, 0, 0, 0, 0, 0, -1)))
    end = int(time.mktime((2006, 1, 3, 0, 0, 0, 0, 0, -1)))

    print 'rrdtool Python test'
    print 'time start: ',start, ' end: ',end

    rrdtool.create(
        'test.rrd',
        '--start', str(start),
        'DS:speed:GAUGE:60:U:U',
        'RRA:AVERAGE:0.5:1:%s' % (24 * 60),
        'RRA:AVERAGE:0.5:10:%s' % (32 * 24 * 6),
        'RRA:MAX:0.5:1:%s' % (24 * 60),
        'RRA:MAX:0.5:10:%s' % (32 * 24 * 6)
    )
