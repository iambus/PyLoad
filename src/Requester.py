
from URL import *

from cStringIO import StringIO
import re

import Template

import time

import Logger
log = Logger.getLogger()

class Response:
	def __init__(self, decoder = None):
		self.rawbody = None
		self.body = None
		self.headers = None
		self.info = None
		self.url = None
		self.code = None

		self.tree = None

		self.decoder = decoder

	# Lazy decoding
	def make_sure(self):
		if self.body == None and self.decoder != None:
			self.body = self.decoder(self.rawbody)

	def get_body(self):
		self.make_sure()
		return self.body

	def rawfind(self, pattern, n = 0, flag = 0):
		try:
			m = re.search(pattern, self.rawbody, flag)
			if m:
				return m.group(n)
		except Exception, e:
			log.exception(e)

	def find(self, pattern, n = 0, flag = 0):
		self.make_sure()
		try:
			m = re.search(pattern, self.body, flag)
			if m:
				return m.group(n)
		except Exception, e:
			log.exception(e)

	def findall(self, pattern, flag = 0):
		self.make_sure()
		try:
			return re.findall(pattern, self.body, flag)
		except Exception, e:
			log.exception(e)

	# for back compatibility
	find_all = findall

	def xtree(self):
		if self.tree != None:
			return self.tree
		self.make_sure()
		try:
			from lxml import etree
		except ImportError:
			log.warn('Module lxml.etree is not found, try to use xml.etree.ElementTree now. Note that the some xpath feature is not supported by older version of xml.etree.ElementTree.')
			from xml.etree import ElementTree as etree
		try:
			self.tree = etree.fromstring(self.body)
			return self.tree
		except Exception, e:
			log.error("Can't parse response body as XML tree.\nBody: [see debug log]\nReasone: %s" % e)
			log.debug("Can't parse response body as XML tree.\nBody: %s\nReasone: %s" % (self.body, e))

	def xfind(self, xpath):
		tree = self.xtree()
		if tree != None:
			return tree.find(xpath)

	def xfindall(self, xpath):
		tree = self.xtree()
		if tree != None:
			return tree.findall(xpath)

	def xfindtext(self, xpath):
		tree = self.xtree()
		if tree != None:
			return tree.findtext(xpath)

	def save_body(self, path):
		self.make_sure()
		fp = open(path, 'w')
		try:
			fp.write(self.body)
		finally:
			fp.close()



RN_P = re.compile(r'\A(.*)\r\n((?:.+\r\n)+)\r\n((?:.|\r|\n)*)\Z')
RN_HEADER = re.compile(r'([^:\r\n]+):\s?([^\r\n]*)')
N_P = re.compile(r'\A(.*)\n((?:.+\n)+)\n((?:.|\r|\n)*)\Z')
N_HEADER = re.compile(r'([^:\n]+):\s?([^\n]*)')

class Requester:
	def __init__(self, url, reqstr = None):
		self.url = url
		self.reqstr = reqstr

		if reqstr != None:
			self.parse()
	
	def parse(self, reqstr = None):
		if reqstr == None:
			reqstr = self.reqstr

		x = self.parse_r_n(reqstr)
		if x == None:
			x = self.parse_n(reqstr)
		if x == None:
			log.error("Can't parse request:[[[%s]]]" % repr(reqstr))
			return

		(self.request_line, headers_list, self.body) = x
		self.method = re.match(r'\S+', self.request_line).group()

		if self.method == 'GET':
			assert self.body == ''

		headers = {}
		for k, v in headers_list:
			if k.lower() in ('content-length', 'host'):
				continue
			elif k.lower() == 'cookie':
				headers['Cookie'] = v
			else:
				headers[k] = v
		self.headers = headers

	def set_host(self):
		raise NotImplementedError()

	def set_reqstr(self, reqstr):
		self.reqstr = reqstr
		self.parse()

	def play(self, variables = {}):
		url = self.url
		data = self.body
		headers = self.headers

		browser = variables.get('browser')
		cookie = variables.get('cookie')
		if browser and hasattr(browser, 'open'):
			if headers.has_key('Cookie'):
				del headers['Cookie'] # if this line raises Exception, then it may be a muti-threads bug...
			requester = browser.open
		#XXX: maybe not a good idea
		elif browser != None and hasattr(browser, 'urlopen'):
			if headers.has_key('Cookie'):
				del headers['Cookie']
			requester = browser.open
		elif cookie != None and isinstance(cookie, CookieJar):
			if headers.has_key('Cookie'):
				del headers['Cookie']
			requester = get_requester(cookie)
		else:
			requester = get_requester()

		if data:
			req = Request(url=url, data=data, headers=headers)
		else:
			req = Request(url=url, headers=headers)

		start_time = time.clock() #XXX: is it a good place?
		try:
			resp = requester(req)
		except URL_ERROR, e:
			log.error('Request error: %s\nURL: %s\nHeaders: %s\n<%s> %s' % (req, url, headers, e.__class__.__name__, e))
			from Errors import TerminateRequest
			#TODO: add trace information
			raise TerminateRequest(e)
		except STATUS_LINE_ERROR, e:
			log.error('Request error when requesting %s\nHeaders: %s\n%s:%s' % (url, headers, e, e.line))
			from Errors import TerminateRequest
			#TODO: add trace information
			raise TerminateRequest('%s:%s' % (e.__class__.__name__, e))
		end_time = time.clock() #XXX: is it a good place?
		rawbody = resp.read()
		# XXX: Is it necessary?
		resp.close()

		response = Response()
		response.rawbody = rawbody
		response.body = None
		response.url = resp.geturl()
		#TODO: recover these attributes here after URL2 supports
		#response.code = resp.code
		#response.info = resp.info()
		#response.headers = resp.info().headers
		return (response, start_time, end_time)

	def parse_r_n(self, reqstr):
		m = RN_P.match(reqstr)
		if m == None:
			return
		request_line = m.group(1)
		headers = RN_HEADER.findall(m.group(2))
		body = m.group(3)
		return (request_line, headers, body)

	def parse_n(self, reqstr):
		m = N_P.match(reqstr)
		if m == None:
			log.error("Can't parse request:[[[%s]]]" % repr(reqstr))
			return
		request_line = m.group(1)
		headers = N_HEADER.findall(m.group(2))
		body = m.group(3)
		return (request_line, headers, body)


if __name__ == '__main__':
	r = Requester('x')
	r.parse('''GET / HTTP/1.0\r
host: localhost:8000\r
connection: close\r
user-agent: Python-urllib/1.17\r
\r
body''')


