
import os
import os.path
import time
import datetime

#TODO: thread-safe
def uuid():
	i = 0
	while i < 999999:
		yield 'u%05d' % i
		i = i + 1
	assert False, 'Max uuid reached'

guuid = uuid()

class PropertyMixin:
	def __init__(self, root = '.'):
		self.uuid = guuid.next()
		self.time = datetime.datetime.now()
		self.timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
		self.label = self.timestr
		self.foldername = self.time.strftime('%Y%m%d-%H%M%S') + ('-%06d-%s' % (self.time.microsecond, self.uuid))
		self.filename = self.time.strftime('%Y%m%d-%H%M%S') + ('-%06d-%s.txt' % (self.time.microsecond, self.uuid))
		self.rootdir = root
	
	def make_folder(self):
		os.makedirs(self.this_folder())

	def make_file(self, content):
		fp = open(self.this_file(), 'wb')
		fp.write(content)
		fp.close()
	
	def this_folder(self):
		return os.path.join(self.rootdir, self.foldername)

	def this_file(self):
		return os.path.join(self.rootdir, self.filename)


class Hit(PropertyMixin):
	def __init__(self, page, root = '.'):
		PropertyMixin.__init__(self)
		self.page = page
		self.reqstr = None
		self.respstr = None

	def save(self):
		#TODO: save the correct content
		self.make_file('hi')

class Page():
	def __init__(self, path):
		self.uuid = guuid.next()
		self.time = None
		self.path = path
		self.label = path
		self.hits = []

	def add_hit(self, hit):
		# Return True if this hit is in page
		if self.path == hit.page:
			self.hits.append(hit)
			if self.time == None:
				self.time = datetime.datetime.now()
				self.timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
			return True
		else:
			return False

class Record(PropertyMixin):
	def __init__(self, root = '.'):
		PropertyMixin.__init__(self, root)
		self.hits = []
		self.pages = []
	
	def add_hit(self, hit):
		# Return True if page alread exists
		hit.rootdir = self.this_folder()
		self.hits.append(hit)
		if len(self.pages) and self.pages[-1].add_hit(hit):
			return True
		else:
			p = Page(hit.page)
			p.add_hit(hit)
			self.pages.append(p)
			return False

	def last_page(self):
		assert len(self.pages), 'There is no page yet!'
		return self.pages[-1]

	def save(self):
		self.make_folder()
		for h in self.hits:
			h.save()

if __name__ == '__main__':
	r = Record('rs')
	r.add_hit(Hit('localhost'))
	r.save()

	print r.uuid
	print r.time
	print r.label
	print r.foldername
	print r.filename
	print r.hits[0].this_file()


