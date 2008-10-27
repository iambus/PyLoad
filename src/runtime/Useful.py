
import cookielib, urllib2

__all__ = ['Cookie', 'Browser', 'sleep']

def Cookie():
	return cookielib.CookieJar()

def Browser():
	import proxy.Settings
	proxy_handler = proxy.Settings.get_proxy_hander()

	cj = cookielib.CookieJar()
	return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), proxy_handler)

from time import sleep

