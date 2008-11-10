
from proxy import Proxy

from Record import HitData

def callback(hit):
	if len(hit.oreqstr) > 100 * 1000:
		print '--------------------------------------------------'
		print 'Requst too large:'
		print 'URL:', hit.url
		print 'Size:', len(hit.oreqstr)
		print hit.reqstr
	if len(hit.orespstr) > 100 * 1000:
		print '--------------------------------------------------'
		print 'Response too large:'
		print 'URL:', hit.url
		print 'Size:', len(hit.orespstr)

def start():
	from Project import Project
	import Record

	project = Project()
	record = Record.Record()

	Proxy.begin_catch(
			#callback = record.add_hit,
			callback = callback,
			filter = lambda x: True,
			hittype = HitData,
			)
	proxy = Proxy.thread_start()

	while True:
		c = raw_input('Enter stop to stop > ')
		if c == 'stop':
			break

	Proxy.stop()
	proxy.join()

	print 'Recording finished'
	print

#	for p in record:
#		for h in p:
#			callback(h)


if __name__ == '__main__':
	start()

