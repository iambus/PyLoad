
try:
	from URL_C import *
except ImportError, e:
	print "[Warning] Can't import URL_C because of %s, use URL_LIB instead" % e
	from URL_LIB import *

