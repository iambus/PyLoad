
USE_AGENT = False
if USE_AGENT:
	try:
		import twisted
	except ImportError:
		print "[Warning] Can't find twisted library. Agent is disabled."
		USE_AGENT = False

AGENT_HOST = 'localhost'
AGENT_PORT = 9107

PROXY_SELF = True # for debug usage

def get_proxy():
	if PROXY_SELF:
		from Proxy import use_port as port
		return 'http://localhost:%s/' % port
	elif USE_AGENT:
		return 'http://%s:%s/' % (AGENT_HOST, AGENT_PORT)
	else:
		return None

def get_proxy_hander():
	http = get_proxy()
	if http:
		from URL import ProxyHandler
		return ProxyHandler(http)
	else:
		return None

