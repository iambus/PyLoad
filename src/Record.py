
import os
import os.path
import time
import datetime

from Player import Player
from Request import Request
import Template
import Coder

import Logger
log = Logger.getLogger()

from Repository import uuid, register

class PropertyMixin:
	def __init__(self):
		self.uuid = uuid()
		self.time = datetime.datetime.now()
		self.timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
		self.label = self.timestr
		self.foldername = self.time.strftime('%Y%m%d-%H%M%S') + ('-%06d-%s' % (self.time.microsecond, self.uuid))
		self.filename = self.foldername + '.txt'

		# TODO: bad place to register
		register(self.uuid, self)


class Hit(PropertyMixin, Player):
	def __init__(self, page):
		PropertyMixin.__init__(self)
		Player.__init__(self)
		self.page = page
		self.reqstr = None
		self.respstr = None

		self.reqcoder = Coder.EmptyCoder
		self.respcoder = Coder.EmptyCoder

	def finish(self):
		# TODO: detect coders
		self.oreqstr = self.reqstr
		self.orespstr = self.respstr
		self.reqstr = self.reqcoder.decode(self.reqstr)
		self.reqstr = Template.escape(self.reqstr)
		if self.respstr:
			self.respstr = self.respcoder.decode(self.respstr)

		self.request = Request(self.page, self.reqstr)

	def get_reqstr(self):
		log.debug('get reqstr')
		return self.reqstr

	def set_reqstr(self, reqstr):
		log.debug('set reqstr')
		self.reqstr = reqstr
		self.request.set_reqstr(self.reqcoder.encode(reqstr))

	def playmain(self, basescope=None):
		if basescope == None:
			self.request.play()
		else:
			response = self.request.play(basescope.get_variables())
			response.body = self.respcoder.decode(response.rawbody)
			basescope.assign('response', response)

class Page(Player):
	def __init__(self, path):
		Player.__init__(self)
		self.uuid = uuid()
		self.time = None
		self.path = path
		self.label = path
		self.hits = []
		self.childern = self.hits

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

class Record(PropertyMixin, Player):
	def __init__(self):
		PropertyMixin.__init__(self)
		Player.__init__(self)
		self.hits = []
		self.pages = []
		self.childern = self.pages
	
	def add_hit(self, hit):
		# Return True if page alread exists
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


if __name__ == '__main__':
	r = Record('rs')
	r.add_hit(Hit('localhost'))

	print r.uuid
	print r.time
	print r.label
	print r.foldername
	print r.filename
	print r.hits[0].this_file()


