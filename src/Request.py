
import urllib2
import cookielib

from cStringIO import StringIO
import re

import Template

import Logger
log = Logger.getLogger()

class Response:
	def __init__(self):
		self.rawbody = None
		self.body = None
		self.headers = None


class Request:
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

		(self.request_line, self.headers, self.body) = x
		self.method = re.match(r'\S+', self.request_line).group()

		if self.method == 'GET':
			assert self.body == ''

		headers = {}
		for k, v in headers.items():
			if k.lower() == 'content-length':
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
		reqstr = Template.subst(self.reqstr, variables)
		self.parse(reqstr)

		url = self.url
		data = self.body
		headers = self.headers

		browser = variables.get('browser')
		cookie = variables.get('cookie')
		if browser and hasattr(browser, 'open'):
			if headers.has_key('Cookie'):
				del headers['Cookie']
			requester = browser.open
		#XXX: maybe not a good idea
		elif browser and hasattr(browser, 'urlopen'):
			if headers.has_key('Cookie'):
				del headers['Cookie']
			requester = browser.open
		elif cookie and isinstance(cookie, cookielib.CookieJar):
			if headers.has_key('Cookie'):
				del headers['Cookie']
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
			requester = opener.open
		else:
			requester = urllib2.urlopen

		if data:
			req = urllib2.Request(url=url, data=data, headers=headers)
		else:
			req = urllib2.Request(url=url, headers=headers)

		resp = requester(req)
		rawbody = resp.read()

		response = Response()
		response.rawbody = rawbody
		response.body = rawbody
		response.url = resp.geturl()
		response.info = resp.info()
		response.headers = resp.info().headers
		return response

	def parse_r_n(self, reqstr):
		m = re.match(r'(.*)\r\n((?:.*\r\n)+)\r\n(.*)$', reqstr)
		if m == None:
			return
		request_line = m.group(1)
		headers = re.findall(r'([^:\r\n]+):\s?([^\r\n]*)', m.group(2))
		body = m.group(3)
		return (request_line, headers, body)

	def parse_n(self, reqstr):
		m = re.match(r'(.*)\n((?:.*\n)+)\n(.*)$', reqstr)
		if m == None:
			log.error("Can't parse request:[[[%s]]]" % repr(reqstr))
			return
		request_line = m.group(1)
		headers = re.findall(r'([^:\n]+):\s?([^\n]*)', m.group(2))
		body = m.group(3)
		return (request_line, headers, body)


if __name__ == '__main__':
	r = Request('x')
	r.parse('''GET / HTTP/1.0\r
host: localhost:8000\r
connection: close\r
user-agent: Python-urllib/1.17\r
\r
body''')


