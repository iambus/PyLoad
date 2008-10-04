
import os
import os.path
import time
import datetime

from Player import Player
from Request import Request
import Template
import ContentTypeHandler

import Logger
log = Logger.getLogger()

from Repository import uuid, register

class PropertyMixin:
	def __init__(self):
		self.time = datetime.datetime.now()
		self.timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
		self.label = self.timestr
		self.foldername = self.time.strftime('%Y%m%d-%H%M%S') + ('-%06d-%s' % (self.time.microsecond, self.uuid))
		self.filename = self.foldername + '.txt'


class Hit(Player, PropertyMixin):
	def __init__(self, page):
		Player.__init__(self)
		PropertyMixin.__init__(self)
		self.page = page
		self.reqstr = None
		self.respstr = None
		self.oreqstr = None
		self.orespstr = None

		self.req_hanlder = ContentTypeHandler.ContentTypeHandler()
		self.resp_handler = ContentTypeHandler.ContentTypeHandler()

	def finish(self):
		assert self.oreqstr == None, 'finish twice!.'
		# TODO: detect coders
		self.oreqstr = self.reqstr
		self.orespstr = self.respstr

		self.req_handler = ContentTypeHandler.get_handler(self.reqstr)
		if self.respstr:
			self.resp_handler = ContentTypeHandler.get_handler(self.respstr)

		self.reqstr = self.req_handler.coder.decode(self.reqstr)
		self.reqstr = Template.escape(self.reqstr)
		if self.respstr:
			self.respstr = self.resp_handler.coder.decode(self.respstr)

		self.request = Request(self.page, self.reqstr)

	def get_reqstr(self):
		log.debug('get reqstr')
		return self.reqstr

	def set_reqstr(self, reqstr):
		log.debug('set reqstr')
		self.reqstr = reqstr
		self.request.set_reqstr(self.req_handler.coder.encode(reqstr))

	def playmain(self, basescope=None):
		if basescope == None:
			self.request.play()
		else:
			response = self.request.play(basescope.get_variables())
			response.body = self.resp_handler.coder.decode(response.rawbody)
			basescope.assign('response', response)

class Page(Player):
	def __init__(self, path):
		Player.__init__(self)
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

class Record(Player, PropertyMixin):
	def __init__(self):
		Player.__init__(self)
		PropertyMixin.__init__(self)
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
	r = Record()
	r.add_hit(Hit('localhost'))

	print r.uuid
	print r.time
	print r.label
	print r.foldername
	print r.filename


