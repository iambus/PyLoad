
import pycurl
from cStringIO import StringIO

URL_ERROR = (pycurl.error)
STATUS_LINE_ERROR = (None)

class Request:
	def __init__(self, url, data = None, headers = None):
		self.url = url
		self.data = data
		self.headers = headers
		if self.headers:
			self.headers = ["%s: %s" % (k, v) for k, v in self.headers.items()]

class Response:
	def __init__(self, url):
		self.url = url
		self.code = None # TODO: set code

		self.stream = StringIO()

		self.body_callback = self.stream.write
#	def body_callback(self):
#		self.stream.write()

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
	c.setopt(c.URL, req.url)
	c.setopt(c.WRITEFUNCTION, resp.body_callback)

	if req.data:
		c.setopt(pycurl.POST, 1)
		c.setopt(pycurl.POSTFIELDS, req.data) 

	if req.headers:
		c.setopt(pycurl.HTTPHEADER, req.headers)

	c.perform()
	c.close()

	return resp


def get_browser(cookie = None):
	raise NotImplementedError('session not implemented')

def get_requester(cookie = None):
	assert cookie == None, 'Cookie is not supported'
	return urlopen

if __name__ == '__main__':
	req = Request('http://www.google.com')
	resp = urlopen(req)
	print resp.read()



