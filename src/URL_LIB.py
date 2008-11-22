
from cookielib import CookieJar

import urllib2
import httplib

URL_ERROR = (urllib2.URLError)
STATUS_LINE_ERROR = (httplib.BadStatusLine)

def ProxyHandler(http, https = None):
	if https:
		return urllib2.ProxyHandler({'http':http, 'https':https})
	else:
		return urllib2.ProxyHandler({'http':http})

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

def get_requester(cookie = None):
	import proxy.Settings
	proxy_handler = proxy.Settings.get_proxy_hander()
	if cookie:
		assert isinstance(cookie, CookieJar)
		if proxy_handler:
			return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), proxy_handler).open
		else:
			return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj)).open
	else:
		if proxy_handler:
			return urllib2.build_opener(proxy_handler).open
		else:
			return urllib2.urlopen


class Request:
	def __init__(self, url, data = None, headers = None):
		pass

Request = urllib2.Request

