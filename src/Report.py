
import sqlite3
import threading
from Queue import Queue

class Report:
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

	def start(self, hits = (), summary = ''):
		self.finished = False
		self.queue = Queue()

		reporter = self
		class ReporterThread(threading.Thread):
			def __init__(self, name='ReporterThread'):
				threading.Thread.__init__(self, name=name)
			def run(self):
				reporter.run(hits, summary)
		thread = ReporterThread() 
		thread.start()

		self.thread = thread
		return thread

	def run(self, hits, summary):
		self.init_report(hits, summary)
		self.receive()
		self.close_report()

	def init_report(self, hits, summary):
		if self.path != ':memory:':
			import os, os.path
			if os.path.exists(self.path):
				os.remove(self.path)
		self.connection = sqlite3.connect(self.path)
		cursor = self.connection.cursor()

		cursor.execute('create table info (key, content)')
		cursor.execute('insert into info(key, content) values (?, ?)', ('summary', summary))

		cursor.execute('create table hits_info (hitid, label, url)')
		for hit in hits:
			cursor.execute('insert into hits_info(hitid, label, url) values (?, ?, ?)', hit)

		cursor.execute('create table hits (hitid, start timestamp, end timestamp)')
		cursor.execute('create table hits_v (hitid, time timestamp, response_time)')

		cursor.close()


	def close_report(self):
		self.connection.commit()
		self.connection.close()

	def receive(self):
		while not self.finished or not self.queue.empty():
			hits = self.queue.get()
			if hits:
				self.add_hits(hits)
			self.queue.task_done()
		assert self.queue.empty()

	def add_hits(self, hits):
		self.connection.executemany('insert into hits(hitid, start, end) values (?, ?, ?)', hits)
		hits_v = []
		for hit in hits:
			a = hit[0]
			b = hit[1] + (hit[2] - hit[1]) / 2
			v = hit[2] - hit[1]
			c = v.seconds * 1000 + v.microseconds/1000
			hits_v.append((a, b, c))
		self.connection.executemany('insert into hits_v(hitid, time, response_time) values (?, ?, ?)', hits_v)

	def post_hits(self, hits):
		if not self.finished:
			self.queue.put(hits)

	def finish(self):
		self.queue.put(None)
		self.finished = True
		self.thread.join()
		self.queue.join()

		self.connection = None
		self.thread = None
		self.queue = None

	def display(self):
		if self.path != ':memory:':
			self.connection = sqlite3.connect(self.path)
			for row in self.connection.execute('select * from hits'):
				print row
			self.connection.close()

	def get_reporter(self):
		return ReportPoster(self)


class ReportPoster:
	# not thread-safe
	def __init__(self, report):
		self.report = report
		self.data = []
	def post_hit(self, id, start, end):
		self.data.append((id, start, end))
	def commit(self):
		self.report.post_hits(self.data)
		self.data = []

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
