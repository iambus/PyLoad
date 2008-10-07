
import cookielib, urllib2

def Cookie():
	return cookielib.CookieJar()

def Browser():
	cj = cookielib.CookieJar()
	return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


