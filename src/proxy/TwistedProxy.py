
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
import sys
log.startLogging(sys.stdout)

class ProxyFactory(http.HTTPFactory):
    def __init__(self):
        http.HTTPFactory.__init__(self)
        self.protocol = proxy.Proxy

import Settings

reactor.listenTCP(Settings.AGENT_PORT, ProxyFactory())
reactor.run()


