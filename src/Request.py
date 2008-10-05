
import urllib2
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

	def set_host(self):
		raise NotImplementedError()

	def set_reqstr(self, reqstr):
		log.debug('set_reqstr:%s' % reqstr)
		self.reqstr = reqstr
		self.parse()

	def play(self, variables = {}):
		reqstr = Template.subst(self.reqstr, variables)
		self.parse(reqstr)
		log.debug('body:%s' % self.body)

		req = self.construct_request()
		resp = urllib2.urlopen(req)
		rawbody = resp.read()

		response = Response()
		response.rawbody = rawbody
		response.body = rawbody
		response.url = resp.geturl()
		response.info = resp.info()
		response.headers = resp.info().headers
		return response

	def construct_request(self):
		# TODO: handle cookie
		url = self.url
		data = self.body
		headers = dict(filter(lambda kv: kv[0].lower() != 'content-length', self.headers))
		if data:
			return urllib2.Request(url=url, data=data, headers=headers)
		else:
			return urllib2.Request(url=url, headers=headers)

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


