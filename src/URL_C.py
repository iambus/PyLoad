
# URL implemented using pycurl

import pycurl
from cStringIO import StringIO

URL_ERROR = (pycurl.error)
STATUS_LINE_ERROR = (None)

from proxy.Settings import get_proxy
http_proxy = get_proxy()

# TODO: is there memory cookie?
class CookieJar:
	def __init__(self):
		# XXX: a better way to generate a temp file name?
		import tempfile
		import os
		fd, path = tempfile.mkstemp(suffix = '.txt', prefix = 'pyload-cookie-')
		fp = os.fdopen(fd, 'wb')
		fp.close()
		self.path = path

class Request:
	def __init__(self, url, data = None, headers = None):
		self.url = url
		self.data = data
		self.headers = headers
		if self.headers:
			self.headers = ["%s: %s" % (k, v) for k, v in self.headers.items()]
		self.cookie = None

class Response:
	def __init__(self, url):
		self.url = url
		self.code = None # TODO: set code

		self.stream = StringIO()
		self.body_callback = self.stream.write

	def read(self):
		content = self.stream.getvalue()
		self.stream.close()
		return content

	def close(self):
		pass

	def geturl(self):
		return self.url

	def info(self):
		raise NotImplementedError()

def urlopen(req):

	resp = Response(req.url)

	c = pycurl.Curl()
	c.setopt(c.URL, req.url.encode())
	c.setopt(c.WRITEFUNCTION, resp.body_callback)

	if req.data:
		c.setopt(pycurl.POST, 1)
		c.setopt(pycurl.POSTFIELDS, req.data) 

	if req.headers:
		c.setopt(pycurl.HTTPHEADER, req.headers)

	if req.cookie:
		c.setopt(pycurl.COOKIEFILE, req.cookie.path)
		c.setopt(pycurl.COOKIEJAR, req.cookie.path)

	if http_proxy:
		c.setopt(pycurl.PROXY, http_proxy)

	c.perform()
	c.close()

	return resp

class Browser:
	def __init__(self, cookie = None):
		self.cookie = cookie or CookieJar()
	def open(self, req):
		req.cookie = self.cookie
		return urlopen(req)

class ProxyHandler:
	def __init__(http, https = None):
		self.http = http
		self.https = https

def get_browser(cookie = None):
	return Browser(cookie)

def get_requester(cookie = None):
	if cookie:
		return Browser(cookie).open
	else:
		return urlopen

if __name__ == '__main__':
	req = Request('http://www.google.com')
	resp = urlopen(req)
	print resp.read()



