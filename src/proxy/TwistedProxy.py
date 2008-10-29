
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.internet.error import CannotListenError

import Settings

import sys

class ProxyFactory(http.HTTPFactory):
    def __init__(self):
        http.HTTPFactory.__init__(self)
        self.protocol = proxy.Proxy

def start_proxy():
	#log.startLogging(sys.stdout)
	try:
		reactor.listenTCP(Settings.AGENT_PORT, ProxyFactory())
		reactor.run()
	except CannotListenError:
		print 'Warning: the port is in use, maybe another agent'

def start():
	raise NotImplementedError()

def stop():
	raise NotImplementedError()

PROCESS = None

def fork():
	if not Settings.USE_AGENT:
		return
	global PROCESS
	assert PROCESS == None
	import subprocess
	PROCESS = subprocess.Popen('python -c "import proxy.TwistedProxy as proxy; proxy.start_proxy()"', shell=False)
	# TODO: check return value
	return PROCESS

def fork_if():
	global PROCESS
	if PROCESS == None:
		fork()

def kill():
	if not Settings.USE_AGENT:
		return
	global PROCESS
	assert PROCESS != None
	import subprocess
	p = subprocess.Popen("taskkill /F /PID %i" % PROCESS.pid, shell=False)
	#p.wait()
	#PROCESS.wait()
	PROCESS = None
	# TODO: check return values

def kill_if():
	global PROCESS
	if PROCESS != None:
		kill()

if __name__ == '__main__':
	start_proxy()

