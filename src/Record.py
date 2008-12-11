
import datetime
import re

from Scope import Scope
from Player import Player
from Requester import Requester
import Template
import ContentTypeHandler

import Errors

import Logger
log = Logger.getLogger()

from Repository import uuid, register

CANCELLED = False

#FIXME: bad name, and bad existence
class PropertyMixin:
	def __init__(self):
		self.time = datetime.datetime.now()
		self.timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
		self.label = self.timestr

class HitData:
	def __init__(self, url):
		self.url = url
		self.reqstr = None
		self.respstr = None

	def finish(self):
		self.oreqstr = self.reqstr
		self.orespstr = self.respstr

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

		self.req_handler = ContentTypeHandler.ContentTypeHandler()
		self.resp_handler = ContentTypeHandler.ContentTypeHandler()

	def finish(self):
		assert self.oreqstr == None, 'finish twice!'

		self.oreqstr = self.reqstr
		self.orespstr = self.respstr
		# TODO: don't decode big response
		if self.respstr and len(self.respstr) > 1*1000*1000:
			log.warning('The response content is too large! Length: %d' % len(self.respstr))
#			self.respstr = None

		self.req_handler = ContentTypeHandler.get_handler(self.reqstr)
		if self.respstr:
			self.resp_handler = ContentTypeHandler.get_handler(self.respstr)

		self.reqstr = self.decode_whole(self.reqstr, self.req_handler.coder)
		self.reqstr = Template.escape(self.reqstr)
		if self.respstr:
			self.respstr = self.decode_whole(self.respstr, self.resp_handler.coder)


		self.set_label()

	def get_reqstr(self):
		return self.reqstr

	def set_reqstr(self, reqstr):
		self.reqstr = reqstr

	def set_host(self, host):
		import urlparse
		parts = list(urlparse.urlsplit(self.url))
		parts[1] = host
		self.url = urlparse.urlunsplit(parts)

	def set_label(self):
		#TODO: generalize it
		import re
		m = re.search(r'<member [^<>]*name="operation">([^<>]+)</member>', self.reqstr)
		if m:
			self.label = m.group(1)

	def play(self, basescope = None):
		if basescope == None:
			basescope = Scope()
		if CANCELLED:
			raise Errors.TerminateUser('User cancelled')
		try:
			self.before(basescope)
			value = self.playmain(basescope)
			self.after(basescope)
			return value
		except Errors.TerminateRequest, e:
			log.exception('Request terminated because of %s' % e)

	def playmain(self, basescope):
		assert basescope != None

		request = self.get_request(basescope)

		response, start_time, end_time = request.play(basescope.get_variables())

		# Lazy decoding
		#response.body = self.decode_body(response.rawbody, self.resp_handler.coder)
		response.decoder = self.resp_handler.coder.decode

		basescope.assign('response', response)
		reporter = basescope.lookup('reporter')
		if reporter:
			reporter.post_hit(self.uuid, start_time, end_time)

		try:
			self.validate_response(response)
		except Errors.ValidationError, e:
			if reporter:
				reporter.post_error(self.uuid, start_time) # using start time
			raise Errors.TerminateRequest('ValidationError: %s' % e)

		return (start_time, end_time)

	def get_original_request_data(self, basescope):
		return self.oreqstr

	def get_original_request(self, basescope):
		return Requester(self.url, self.oreqstr)

	def get_cached_request_data(self, basescope):
		cache = basescope.lookup('cache')
		if cache != None:
			if cache == 0:
				self.cached_request = self.get_encoded_request_data(basescope)
				basescope.assign('cache', 1)
			return self.cached_request
		else:
			return self.get_encoded_request_data(basescope)

	def get_cached_request(self, basescope):
		cache = basescope.lookup('more_cache')
		if cache != None:
			if cache == 0:
				self.cached_request = self.get_encoded_request(basescope)
				basescope.assign('more_cache', 1)
			return self.cached_request
		else:
			return self.get_encoded_request(basescope)

	def get_encoded_request_data(self, basescope):
		variables = basescope.get_variables()
		reqstr = Template.subst(self.reqstr, variables)
		return self.encode_whole(reqstr, self.req_handler.coder)

	def get_encoded_request(self, basescope):
		return Requester(self.url, self.get_encoded_request_data(basescope))

	# by default, always encode request
	get_request = get_encoded_request

	# change to get_original_request if the recorded request is OK for you
	#get_request = get_original_request

	# change to get_cached_request if the recorded request is not OK for you,
	# but all requests sent during one test are exactly the same
	#get_request = get_cached_request

	# {{{ encode / decode
	def decode_whole(self, raw, coder):
		header, body = self.split_header_and_body(raw)
		return header + coder.decode(body)
	def decode_body(self, body, coder):
		return coder.decode(body)
	def encode_whole(self, exp, coder):
		header, body = self.split_header_and_body(exp)
		rawbody = coder.encode(body)
		if type(rawbody) == unicode:
			# FIXME: Not good
			rawbody = rawbody.encode('utf-8')
		assert type(rawbody) == str
		# FIXME: Not good
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
	# }}}

	def validate_response(self, response):
		handler = self.resp_handler or self.req_handler
		if len(handler) == 2:
			# older version of ContentTypeHandler doesn't have validators
			# for back compatibility, we re-set handlers
			self.req_handler = ContentTypeHandler.get_handler(self.oreqstr)
			if self.orespstr:
				self.resp_handler = ContentTypeHandler.get_handler(self.orespstr)
			handler = self.resp_handler or self.req_handler

		handler.validator.validate(response)


class Page(Player):
	def __init__(self, path):
		Player.__init__(self)
		self.time = datetime.datetime.now()
		self.timestr = self.time.strftime('%Y-%m-%d %H:%M:%S')
		self.path = path
		self.label = path
		self.hits = []
		self.childern = self.hits

	def add_hit(self, hit):
		# Return True if this hit is in page
		if self.path == hit.page:
			self.hits.append(hit)
			return True
		else:
			return False

	def set_host(self, host):
		for h in self.hits:
			h.set_host(host)

	def playmain(self, basescope):
		times = []
		for hit in self.hits:
			value = hit.play(Scope(basescope))
			# TODO: record page errors
			if value:
				times.append(value)
		reporter = basescope.lookup('reporter')
		if reporter and times:
			starts, ends = zip(*times)
			start_time = min(starts)
			end_time = max(ends)
			response_time = sum(map(lambda x:int((x[1]-x[0])*1000), times))
			reporter.post_page(self.uuid, start_time, end_time, response_time)

class Record(Player, PropertyMixin):
	def __init__(self):
		Player.__init__(self)
		PropertyMixin.__init__(self)
		self.pages = []
		self.childern = self.pages
	
	def add_hit(self, hit):
		# Return True if page alread exists
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

	def set_host(self, host):
		for p in self.pages:
			p.set_host(host)


if __name__ == '__main__':
	r = Record()
	r.add_hit(Hit('localhost'))

	print r.uuid
	print r.time
	print r.label


# vim: foldmethod=marker:
