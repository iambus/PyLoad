
USE_AGENT = True
if USE_AGENT:
	try:
		import twisted
	except ImportError:
		print "[Warning] Can't find twisted library. Agent is disabled."
		USE_AGENT = False

AGENT_HOST = 'localhost'
AGENT_PORT = 9107

def get_proxy():
	http_proxy = 'http://%s:%s/' % (AGENT_HOST, AGENT_PORT)
	return {'http': http_proxy}

def get_proxy_hander():
	if USE_AGENT:
		import urllib2
		return urllib2.ProxyHandler(get_proxy())
	else:
		return None

