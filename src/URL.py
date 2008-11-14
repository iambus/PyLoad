
from cookielib import CookieJar

import urllib2
import httplib

URL_ERROR = (urllib2.URLError)
STATUS_LINE_ERROR = (httplib.BadStatusLine)

def get_browser(cookie = None):
	import proxy.Settings
	proxy_handler = proxy.Settings.get_proxy_hander()
	if cookie:
		assert isinstance(cookie, CookieJar)
		if proxy_handler:
			return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), proxy_handler)
		else:
			return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	else:
		if proxy_handler:
			return urllib2.build_opener(proxy_handler)
		else:
			return urllib2.build_opener()

class Request:
	def __init__(self, url, data = None, headers = None):
		pass

Request = urllib2.Request

