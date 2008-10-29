
import cookielib, urllib2

__all__ = ['Cookie', 'Browser', 'sleep']

def Cookie():
	return cookielib.CookieJar()

def Browser():
	import proxy.Settings
	proxy_handler = proxy.Settings.get_proxy_hander()

	cj = cookielib.CookieJar()
	if proxy_handler:
		return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), proxy_handler)
	else:
		return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

from time import sleep

