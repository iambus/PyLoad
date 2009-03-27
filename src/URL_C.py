
# URL implemented using pycurl

import pycurl
from cStringIO import StringIO

URL_ERROR = (pycurl.error)
STATUS_LINE_ERROR = (None)

from proxy.Settings import get_proxy
http_proxy = get_proxy()


class FileCookieJar:
	def __init__(self):
		# XXX: a better way to generate a temp file name?
		import tempfile
		import os
		fd, path = tempfile.mkstemp(suffix = '.txt', prefix = 'pyload-cookie-')
		fp = os.fdopen(fd, 'wb')
		fp.close()
		self.path = path

	def apply_to(self, c):
		c.setopt(pycurl.COOKIEFILE, self.path)
		c.setopt(pycurl.COOKIEJAR, self.path)

# XXX: How about the performance of pycurl.CurlShare?
class MemoryCookieJar:
	def __init__(self):
		self.shared = pycurl.CurlShare()
		self.shared.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_COOKIE)
	def apply_to(self, c):
		c.setopt(pycurl.SHARE, self.shared)

CookieJar = MemoryCookieJar

class Request:
	def __init__(self, url, data = None, headers = None):
		#assert headers == None or type(headers) == dict
		self.url = url
		self.data = data
		self.headers = headers
		if self.headers:
			self.headers = ["%s: %s" % (k, v) for k, v in self.headers.items()]
		self.cookie = None

class Response:
	def __init__(self, url):
		self.url = url
		self.code = None

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

def open_with_curl(c, req):

	resp = Response(req.url)

	c.setopt(c.URL, req.url.encode())
	c.setopt(c.WRITEFUNCTION, resp.body_callback)

	if req.data:
		c.setopt(pycurl.POST, 1)
		c.setopt(pycurl.POSTFIELDS, req.data) 

	if req.headers:
		c.setopt(pycurl.HTTPHEADER, req.headers)

	if req.cookie:
		req.cookie.apply_to(c)

	if req.url.startswith('https'):
		# don't verify the authenticity of the peer's certificate
		c.setopt(pycurl.SSL_VERIFYPEER, 0)
		# cache SSL session
		#c.setopt(pycurl.SSL_SESSIONID_CACHE, 0)

	if http_proxy:
		c.setopt(pycurl.PROXY, http_proxy)

	c.perform()
	resp.code = c.getinfo(pycurl.RESPONSE_CODE)

	return resp

def urlopen(req):
	c = pycurl.Curl()
	resp = open_with_curl(c, req)
	c.close()
	return resp

class Browser:
	def __init__(self, cookie = None):
		self.cookie = cookie or CookieJar()
		self.curl_obj = pycurl.Curl()
		self.cookie.apply_to(self.curl_obj)
	def open(self, req):
		return open_with_curl(self.curl_obj, req)

class ProxyHandler:
	def __init__(http, https = None):
		self.http = http
		self.https = https

def get_browser(cookie = None):
	return Browser(cookie)

def get_requester(cookie = None):
	if cookie:
		print '[Warning] Using CookieJar directly is not suggested. Browser object is suggested.'
		return Browser(cookie).open
	else:
		return urlopen

if __name__ == '__main__':
	req = Request('http://www.google.com')
	resp = urlopen(req)
	print resp.read()



