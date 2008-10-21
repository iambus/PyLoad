
import cookielib, urllib2

__all__ = ['Cookie', 'Browser', 'sleep']

def Cookie():
	return cookielib.CookieJar()

def Browser():
	cj = cookielib.CookieJar()
	return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

from time import sleep

