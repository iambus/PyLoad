
import sqlite3
import threading
from Queue import Queue

import time

def remove_file(path):
	import os, os.path
	if os.path.exists(path):
		os.remove(path)

class ReportBase:
	def __init__(self, path = ':memory:'):
		''' The path is the location of SQLite3 database.
			If path is a string, then the database is created on file system specified by this string.
		    If path is None, then a memory databse is used.
			WARNING: before the dabase is created on file system, the old file on this location will be removed first.
		'''
		# members: path, finished, queue, thread, connection
		self.path = path or ':memory:'

		self.finished = False
		self.queue = None


	def init_report(self, hits, pages, info):
		if type(info) == dict:
			info = info.items()
		elif type(info) == tuple or type(info) == list:
			pass
		elif type(info) == str or type(info) == unicode:
			# TODO: remove this clause later
			print '[Warning] info is a string, so use info as summary. Please use update your code to supply a dict/tuple/list next time.'
			info = (('summary', info),)
		else:
			raise TypeError(type(info))

		if self.path != ':memory:':
			try:
				remove_file(self.path)
			except Exception, e:
				print "Can't remove path: %s, Reasone: %s" % (self.path, e)
				self.path += '-1'
				print "Use path %s instead." % self.path
				remove_file(self.path)

		self.connection = sqlite3.connect(self.path)
		cursor = self.connection.cursor()

		# Info
		cursor.execute('create table info (key, content)')
		cursor.executemany('insert into info(key, content) values (?, ?)', info)

		# Hit info
		cursor.execute('create table hits_info (hitid, label, url)')
		for hit in hits:
			cursor.execute('insert into hits_info(hitid, label, url) values (?, ?, ?)', hit)

		# Page info
		cursor.execute('create table pages_info (pageid, label)')
		cursor.execute('create table page_hits (pageid, hitid)')
		for page in pages:
			cursor.execute('insert into pages_info(pageid, label) values (?, ?)', page[:2])
			hitids = page[2]
			for hitid in hitids:
				cursor.execute('insert into page_hits(pageid, hitid) values (?, ?)', (page[0], hitid))

		# Runtime data
		cursor.execute('create table hits (hitid, start timestamp, end timestamp)')
		cursor.execute('''create view hits_v as
				select
					hits.hitid as hitid,
					(start + end)/2 as timestamp,
					(end - start) as response_time
				from hits''')
		cursor.execute('''create view hits_v_start as
				select
					hits.hitid as hitid,
					start as timestamp,
					(end - start) as response_time
				from hits''')
		cursor.execute('''create view hits_v_end as
				select
					hits.hitid as hitid,
					end as timestamp,
					(end - start) as response_time
				from hits''')
		cursor.execute('''create view one as
				select
					hits_v.hitid as id,
					hits_info.label as label,
					hits_v.response_time as time
				from hits_v, hits_info
				where hits_v.hitid = hits_info.hitid''')
		cursor.execute('''create view summary as
				select
					id,
					one.label as label,
					avg(time) as avg,
					max(time) as max,
					min(time) as min,
					count(time) as count
				from one group by id''')

		cursor.execute('create table pages (pageid, start timestamp, end timestamp, response_time)')
		cursor.execute('''create view pages_v as
				select
					pages.pageid as pageid,
					(start + end)/2 as timestamp,
					pages.response_time as response_time
				from pages, pages_info
				where pages.pageid = pages_info.pageid''')
		cursor.execute('''create view pages_v_start as
				select
					pages.pageid as pageid,
					start as timestamp,
					pages.response_time as response_time
				from pages, pages_info
				where pages.pageid = pages_info.pageid''')
		cursor.execute('''create view pages_v_end as
				select
					pages.pageid as pageid,
					end as timestamp,
					pages.response_time as response_time
				from pages, pages_info
				where pages.pageid = pages_info.pageid''')
		cursor.execute('''create view page_one as
				select
					pages_v.pageid as id,
					pages_info.label as label,
					pages_v.response_time as time
				from pages_v, pages_info where pages_v.pageid = pages_info.pageid''')
		cursor.execute('''create view page_summary as
				select
					id,
					page_one.label as label,
					avg(time) as avg,
					max(time) as max,
					min(time) as min,
					count(time) as count
				from page_one group by id''')

		cursor.execute('create table errors (id, time)')
		cursor.execute('''create view error_summary as
				select
					id,
					count(time) as count
				from errors group by id''')

		cursor.close()

	def close_report(self):
		self.connection.commit()
		self.connection.close()

	def receive(self):
		while not self.finished or not self.queue.empty():
			data = self.queue.get()
			if data:
				if len(data[0]) == 3:
					self.add_hits(data)
				elif len(data[0]) == 4:
					self.add_pages(data)
				elif len(data[0]) == 2:
					self.add_errors(data)
				else:
					assert False, 'The length of data must be 2 (for error) 3 (for hit) or 4 (for page), but got: %s' % str(data[0])
			self.queue.task_done()
		assert self.queue.empty()

	def add_hits(self, hits):
		hits2 = []
		for hit in hits:
			id = hit[0]
			start = int((hit[1] - self.start_time)*1000)
			end = int((hit[2] - self.start_time)*1000)
			hits2.append((id, start, end))
		self.connection.executemany('insert into hits(hitid, start, end) values (?, ?, ?)', hits2)

	def add_pages(self, pages):
		pages2 = []
		for page in pages:
			id = page[0]
			start = int((page[1] - self.start_time)*1000)
			end = int((page[2] - self.start_time)*1000)
			time = page[3]
			pages2.append((id, start, end, time))
		self.connection.executemany('insert into pages(pageid, start, end, response_time) values (?, ?, ?, ?)', pages2)

	def add_errors(self, errors):
		errors2 = []
		for error in errors:
			id = error[0]
			time = int(error[1]*1000)
			errors2.append((id, time))
		self.connection.executemany('insert into errors(id, time) values (?, ?)', errors2)

	def post_hits(self, hits):
		if not self.finished:
			self.queue.put(hits)

	def post_pages(self, pages):
		if not self.finished:
			self.queue.put(pages)

	def post_errors(self, errors):
		if not self.finished:
			self.queue.put(errors)

	def display(self):
		if self.path != ':memory:':
			self.connection = sqlite3.connect(self.path)
			for row in self.connection.execute('select * from hits'):
				print row
			self.connection.close()

	def get_reporter(self):
		return ReportPoster(self)


class SimpleReport(ReportBase):
	def __init__(self, path = ':memory:'):
		ReportBase.__init__(self, path)

	def start(self, hits = (), pages = (), info = ()):
		self.finished = False
		self.queue = Queue()
		self.start_time = time.clock()

		self.init_report(hits, pages, info)

	def finish(self):
		self.finished = True
		self.receive()
		self.close_report()
		self.queue.join()

		self.connection = None
		self.queue = None

class ThreadReport(ReportBase):
	def __init__(self, path = ':memory:'):
		ReportBase.__init__(self, path)

	def start(self, hits = (), pages = (), info = ()):
		self.finished = False
		self.queue = Queue()
		self.start_time = time.clock()

		reporter = self
		class ReporterThread(threading.Thread):
			def __init__(self, name='ReporterThread'):
				threading.Thread.__init__(self, name=name)
			def run(self):
				reporter.run(hits, pages, info)
		thread = ReporterThread() 
		thread.start()

		self.thread = thread

	def run(self, hits, pages, info):
		self.init_report(hits, pages, info)
		self.receive()
		self.close_report()

	def finish(self):
		self.queue.put(None)
		self.finished = True
		self.thread.join()
		self.queue.join()

		self.connection = None
		self.thread = None
		self.queue = None


Report = ThreadReport
#Report = SimpleReport

class ReportPoster:
	# not thread-safe
	def __init__(self, report):
		self.report = report
		self.hits_data = []
		self.pages_data = []
		self.errors_data = []
	def post_hit(self, id, start, end):
		self.hits_data.append((id, start, end))
	def post_page(self, id, start, end, time):
		self.pages_data.append((id, start, end, time))
	def post_error(self, id, time):
		self.errors_data.append((id, time))
	def commit(self):
		self.report.post_hits(self.hits_data)
		self.report.post_pages(self.pages_data)
		self.report.post_errors(self.errors_data)
		self.hits_data = []
		self.pages_data = []
		self.errors_data = []

if __name__ == '__main__':
	r = Report('last-report.db')
	import datetime
	start = datetime.datetime.now()
	end   = datetime.datetime.now()
	r.start(hits=(('u0001','name','hehe'),))

	reporter = r.reporter()
	reporter.post_hit('u', start, end)
	reporter.commit()
	r.post_hits((('1',start,end),))
	r.post_hits((('2',start,end),))
	r.post_hits((('3',start,end),))

	r.finish()
	r.display()

#	r.start()
#	r.post_hits((('----',start,end),))
#	r.finish()
#	r.display()

