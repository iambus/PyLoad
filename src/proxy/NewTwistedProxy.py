
from twisted.web import proxy, http
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.error import CannotListenError

#import sys
#log.startLogging(sys.stdout)
log.startLogging(open('twisted-proxy.log', 'w'))

import time

class NewProxyClient(proxy.ProxyClient):

	def handleHeader(self, key, value):
		proxy.ProxyClient.handleHeader(self, key, value)

	def handleResponsePart(self, data):
		proxy.ProxyClient.handleResponsePart(self, data)

	def handleResponseEnd(self):
		proxy.ProxyClient.handleResponseEnd(self)
		self.end_time = time.clock()
		print 'time: %s' % (self.start_time - self.end_time)

	def connectionMade(self):
		print 'connected'
		proxy.ProxyClient.connectionMade(self)
		self.start_time = time.clock()

class NewProxyClientFactory(proxy.ProxyClientFactory):
	def buildProtocol(self, addr):
		client = proxy.ProxyClientFactory.buildProtocol(self, addr)
		client.__class__ = NewProxyClient
		return client

	def clientConnectionFailed(self, connector, reason):
		print "Can't connect, reasone: %s" % reason
		proxy.ProxyClientFactory.clientConnectionFailed(self, connector, reason)
		#self.father.transport.write("HTTP/1.0 501 Gateway error\r\n")
		#self.father.transport.write("Content-Type: text/html\r\n")
		#self.father.transport.write("\r\n")
		#self.father.transport.write('''<H1>Could not connect</H1>''')
		#self.father.transport.loseConnection()


class NewProxyRequest(proxy.ProxyRequest):
	protocols = {'http': NewProxyClientFactory}

	def __init__(self, *args):
		proxy.ProxyRequest.__init__(self, *args)


class NewProxy(proxy.Proxy):
	def __init__(self):
		proxy.Proxy.__init__(self)

	def requestFactory(self, *args):
		return NewProxyRequest(*args)

class NewProxyFactory(http.HTTPFactory):
	def __init__(self):
		http.HTTPFactory.__init__(self)

	def buildProtocol(self, addr):
		protocol = NewProxy()
		return protocol


def start_proxy(port = None):
	#log.startLogging(sys.stdout)
	if port == None:
		import Settings
		port = Settings.AGENT_PORT
	try:
		reactor.listenTCP(port, NewProxyFactory())
		reactor.run()
	except CannotListenError:
		print 'Warning: the port %d is in use, maybe another agent' % port

if __name__ == "__main__":
	start_proxy()

