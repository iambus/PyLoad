
import cookielib, urllib2

__all__ = ['Cookie', 'Browser', 'sleep', 'randsleep', 'uuid']

def Cookie():
	import URL
	return URL.CookieJar()

def Browser():
	import URL
	return URL.Browser()

from time import sleep

def randsleep(n, r = 0.5):
	from random import randint
	ms = randint((n - r) * 1000, (n + r) * 1000)
	sleep(ms/1000.0)

def uuid():
	from uuid import uuid1
	return uuid1()

def log(message):
	import Logger
	logger = Logger.getLogger()
	logger.info(message)


