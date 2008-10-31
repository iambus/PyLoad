
import cookielib, urllib2

__all__ = ['Cookie', 'Browser', 'sleep', 'randsleep']

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

def randsleep(n, r = 0.5):
	from random import randint
	ms = randint((n - r) * 1000, (n + r) * 1000)
	sleep(ms/1000.0)


