
import os
import os.path
import time
import datetime
import re

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
	def __init__(self, url):
		Player.__init__(self)
		PropertyMixin.__init__(self)
		self.url = url
		self.reqstr = None
		self.respstr = None
		self.oreqstr = None
		self.orespstr = None

		#param_index = url.find('?')
		#if param_index != -1:
		#	self.page = url[:param_index]
		#else:
		#	self.page = url
		import re
		m = re.match(r'^https?://[^/]+(.*?)(\?[^/]*)?$', url)
		if m:
			self.page = m.group(1)
		else:
			self.page = url

		self.label = url

		self.req_hanlder = ContentTypeHandler.ContentTypeHandler()
		self.resp_handler = ContentTypeHandler.ContentTypeHandler()

	def finish(self):
		assert self.oreqstr == None, 'finish twice!'
		# TODO: detect coders
		self.oreqstr = self.reqstr
		self.orespstr = self.respstr

		self.req_handler = ContentTypeHandler.get_handler(self.reqstr)
		if self.respstr:
			self.resp_handler = ContentTypeHandler.get_handler(self.respstr)

		self.reqstr = self.decode(self.reqstr, self.req_handler.coder)
		self.reqstr = Template.escape(self.reqstr)
		if self.respstr:
			self.respstr = self.decode(self.respstr, self.resp_handler.coder)

		self.request = Request(self.url, self.oreqstr)

		self.set_label()

	def get_reqstr(self):
		log.debug('get reqstr')
		return self.reqstr

	def set_reqstr(self, reqstr):
		log.debug('set reqstr')
		self.reqstr = reqstr
		self.request.set_reqstr(self.encode(reqstr, self.req_handler.coder))

	def decode(self, raw, coder):
		header, body = self.split_header_and_body(raw)
		return header + coder.decode(body)
	def decode_body(self, body, coder):
		return coder.decode(body)
	def encode(self, exp, coder):
		header, body = self.split_header_and_body(exp)
		rawbody = coder.encode(body)
		assert type(rawbody) == str
		rawheader = header.encode('utf-8')
		return rawheader + rawbody
	def split_header_and_body(self, whole):
		index = whole.find('\r\n\r\n')
		if index != -1:
			index += 4
		else:
			index = whole.find('\n\n')
			if index != -1:
				index += 2
		if index == -1:
			raise RuntimeError("Bad reqest/response format:[%s]" % whole)
		header = whole[0:index]
		body = whole[index:]
		return header, body

	def set_label(self):
		#TODO: generalize it
		import re
		m = re.search(r'<member [^<>]*name="operation">([^<>]+)</member>', self.reqstr)
		if m:
			self.label = m.group(1)

	def playmain(self, basescope=None):
		if basescope == None:
			self.request.play()
		else:
			response, start_time, end_time = self.request.play(basescope.get_variables())
			response.body = self.decode_body(response.rawbody, self.resp_handler.coder)
			basescope.assign('response', response)
			reporter = basescope.lookup('reporter')
			if reporter:
				reporter.post_hit(self.uuid, start_time, end_time)


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


