
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.error import CannotListenError


class ProxyFactory(http.HTTPFactory):
    def __init__(self):
        http.HTTPFactory.__init__(self)
        self.protocol = proxy.Proxy

def start_proxy(port = None):
	import sys
	#log.startLogging(sys.stdout)
	#log.startLogging(open('twisted-proxy.log', 'w'))
	if port == None:
		import Settings
		port = Settings.AGENT_PORT
	try:
		reactor.listenTCP(port, ProxyFactory())
		reactor.run()
	except CannotListenError:
		print 'Warning: the port %d is in use, maybe another agent' % port

def start():
	raise NotImplementedError()

def stop():
	raise NotImplementedError()


if __name__ == '__main__':
	start_proxy()

