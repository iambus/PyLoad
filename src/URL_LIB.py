
# URL implemented using urllib2

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

from proxy.Settings import get_proxy
http_proxy = get_proxy()
# XXX: can a ProxyHandler be shared among threads?
proxy_handler = ProxyHandler(http_proxy) if http_proxy else None

def Browser(cookie = None):
	cj = cookie if cookie != None else CookieJar()
	if proxy_handler:
		return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), proxy_handler)
	else:
		return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

def get_browser(cookie = None):
	if cookie != None:
		assert isinstance(cookie, CookieJar)
		return Browser(cookie)
	else:
		if proxy_handler:
			return urllib2.build_opener(proxy_handler)
		else:
			return urllib2.build_opener()

def get_requester(cookie = None):
	if cookie != None:
		assert isinstance(cookie, CookieJar)
		return Browser(cookie).open
	else:
		if proxy_handler:
			return urllib2.build_opener(proxy_handler).open
		else:
			return urllib2.urlopen


class Request:
	def __init__(self, url, data = None, headers = None):
		pass

Request = urllib2.Request

