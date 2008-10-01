
import urllib2
from cStringIO import StringIO
import re

import Logger
log = Logger.getLogger()

class Request:
	def __init__(self, url, reqstr = None):
		self.url = url
		self.reqstr = reqstr
		if reqstr != None:
			self.parse()
	
	def parse(self, reqstr = None):
		if reqstr == None:
			reqstr = self.reqstr
		m = re.match(r'(.*)\r\n((?:.*\r\n)+)\r\n(.*)$', reqstr)
		if m == None:
			return
		self.request_line = m.group(1)
		self.headers = re.findall(r'([^:\r\n]+):\s?([^\r\n]*)', m.group(2))
		self.body = m.group(3)
		self.method = re.match(r'\S+', self.request_line).group()

	def set_host(self):
		raise NotImplementedError()

	def set_reqstr(self, reqstr):
		self.reqstr = reqstr
		self.parse()

	def play(self, variables = {}):
		# TODO: send real request...
		req = urllib2.Request(url=self.url)
		response = urllib2.urlopen(req)
		respstr = response.read()
		response.respstr = respstr
		return response


if __name__ == '__main__':
	r = Request('x')
	r.parse('''GET / HTTP/1.0\r
host: localhost:8000\r
connection: close\r
user-agent: Python-urllib/1.17\r
\r
body''')


