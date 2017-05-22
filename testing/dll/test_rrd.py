import rrdtool
import os
import time
import random
import math


if os.path.exists('test.rrd'):
	os.remove('test.rrd')

start = int( time.mktime( (2006,1,1,0,0,0,0,0,-1) ) )
end = int( time.mktime( (2006,1,3,0,0,0,0,0,-1) ) )

print 'rrdtool Python test'
print 'time start: ',start, ' end: ',end

print 'creating rrd database ...'
rrdtool.create( 'test.rrd', \
	'--start', str(start), \
	'DS:speed:GAUGE:60:U:U', \
	'RRA:AVERAGE:0.5:1:%s' % (24 * 60), \
	'RRA:AVERAGE:0.5:10:%s' % (32 * 24 * 6), \
	'RRA:MAX:0.5:1:%s' % (24 * 60), \
	'RRA:MAX:0.5:10:%s' % (32 * 24 * 6) )

print 'inserting random sample data ...'
for t in range(start+60,end,60):
	rt = t
	rv = 100 + 10*math.sin((rt-start)/5000) + random.randint(0,25) 
	rrdtool.update( 'test.rrd', '%s:%s' % (rt,rv))

first = rrdtool.first('test.rrd')
print 'time of first sample: ', first, time.localtime( first )
last = rrdtool.last('test.rrd')
print 'time of first sample: ', last, time.localtime( last )

info = rrdtool.info('test.rrd')
print 'database info ...'
for i in info:
	print i, ': ', info[i] 
print

print 'creating graph ...'
rrdtool.graph( \
	'test.png', \
	'--start', str(start), \
	'--end', str(end), \
	'--width', '800', \
	'--height', '400', \
	'DEF:aspeed=test.rrd:speed:AVERAGE:step=600', \
	'AREA:aspeed#800000', \
	'DEF:mspeed=test.rrd:speed:MAX:step=600', \
	'LINE2:mspeed#FF0000' )

print 'show graph ...'
os.system('test.png')

print 'done !'


