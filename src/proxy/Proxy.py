
if __name__ == '__main__':
    import sys
    sys.path.append('..')

import BaseHTTPServer, select, socket, SocketServer, urlparse

import cStringIO

from Filter import EmptyFilter, DefaultContentFilter, DefaultRuleFilter
import Logger
log = Logger.getLogger()

HitType = None
class EmptyHit:
    def finish(self):
        pass

# FIXME: too bad code...
reqfilter = DefaultRuleFilter()
respfilter = EmptyFilter()
respcallback = lambda x: False

running = 1

default_port = 9008
use_port = default_port

STOPPING_URL = 'http://stop.it:0/'

class StoppingFlag(Exception):
	pass

class ProxyHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    rbufsize = 0                        # self.rfile Be unbuffered

    def init(self):
        log.debug('init:%s' % self)
        if self.path == STOPPING_URL:
            raise StoppingFlag()
        if reqfilter.test(self.path):
            self.hit = EmptyHit()
        else:
            self.hit = HitType(self.path)
        #TODO: thread-safe

        self.reqstr = cStringIO.StringIO()
        self.respstr = None

    def end(self):
        log.debug('end:%s' % self)
        self.hit.reqstr = self.reqstr.getvalue()
        assert self.hit.reqstr, 'You got an emtpy request?'
        self.reqstr.close()
        if self.respstr:
            self.hit.respstr = self.respstr.getvalue()
            assert self.hit.respstr, 'You got an emtpy response?'
            self.respstr.close()
        else:
            self.hit.respstr = None
        self.hit.finish() # XXX: is it a correct place to finish?
        # XXX: bad code
        if not isinstance(self.hit, EmptyHit):
            global respcallback
            respcallback(self.hit)

    def req(self, data):
        self.reqstr.write(data)

    def resp(self, data):
        assert isinstance(data, basestring)
        global respfilter
        if self.respstr:
            self.respstr.write(data)
        elif not respfilter.test(data):
            self.respstr = cStringIO.StringIO()
            self.respstr.write(data)

    def reqinfo(self, host, port):
        self.hit.reqhost = host
        self.hit.reqport = port

    def respinfo(self, host, port):
        self.hit.resphost = host
        self.hit.respport = port


    def handle(self):
        (ip, port) =  self.client_address
        if hasattr(self, 'allowed_clients') and ip not in self.allowed_clients:
            self.raw_requestline = self.rfile.readline()
            if self.parse_request(): self.send_error(403)
        else:
            try:
                self.__base_handle()
            except StoppingFlag:
                pass

    def _connect_to(self, netloc, sock):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i+1:])
        else:
            host_port = netloc, 80
        log.debug("connect to %s:%d" % host_port)
        self.reqinfo(*host_port)
        try: sock.connect(host_port)
        except socket.error, arg:
            try: msg = arg[1]
            except: msg = arg
            self.send_error(404, msg)
            return 0
        return 1

    def do_CONNECT(self):
        #assert False, 'Never happen'
        log.info('do_CONNECT:'+self.path)
        self.init()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.debug('connection:%s' % self.connection)
        log.debug('socket:%s' % sock)
        try:
            if self._connect_to(self.path, sock):
                log.info(self.address_string()+':'+self.requestline+' 200')
                self.wfile.write(self.protocol_version +
                                 " 200 Connection established\r\n")
                self.wfile.write("Proxy-agent: %s\r\n" % self.version_string())
                self.wfile.write("\r\n")
                self._read_write(sock, 300)
                self.end()
            else:
                log.error("What's wrong?")
        finally:
            log.debug("Bye")
            sock.close()
            self.connection.close()

    def do_REQ(self):
        log.debug('do_REQ:'+self.path)
        self.init()
        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.debug('connection:%s' % self.connection)
        log.debug('socket:%s' % sock)
        try:
            if self._connect_to(netloc, sock):
                log.info(self.address_string()+':'+self.requestline)
                

                self.req("%s %s %s\r\n" % (
                    self.command,
                    urlparse.urlunparse(('', '', path, params, query, '')),
                    self.request_version))
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                del self.headers['Accept-Encoding'] # Disable Gzip. TODO: support gzip
                for key_val in self.headers.items():
                    self.req("%s: %s\r\n" % key_val)
                self.req("\r\n")
                self.respinfo(*sock.getpeername())
                sock.send(self.reqstr.getvalue())
                self._read_write(sock)
                self.end()
            else:
                log.error("What's wrong?")
        finally:
            log.debug("bye")
            sock.close()
            self.connection.close()

    def _read_write(self, sock, max_idling=20):
        iw = [self.connection, sock]
        ow = []
        count = 0
        while 1:
            if len(iw) == 0:
                break
            if len(iw) == 1 and iw[0] is self.connection and count >= 0:
                log.warn("We don't wait client connection any more")
                break
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs: break
            if ins:
                for i in ins:
                    try:
                        data = i.recv(8192)
                    except socket.error, e:
                        log.exception(e)
                        iw.remove(i)
                        continue
                    if len(data) == 0:
                        log.warn('remove socket:%s' % i)
                        iw.remove(i)
                        continue
                    if i is sock:
                        self.resp(data)
                        self.connection.send(data)
                    elif i is self.connection:
                        log.warn('Received new data from client. Length: %d' % len(data))
                        self.req(data)
                        sock.send(data)
                    else:
                        assert False, 'select nothing...'
                    count = 0
            else:
                # Idle...
                count += 1
                log.debug("idle%3d" % count)
            if count >= max_idling:
                log.error('Max idling: %d' % count)
                # don't break
                #break

    do_GET    = do_REQ
    do_POST   = do_REQ
    do_HEAD   = do_REQ
    do_PUT    = do_REQ
    do_DELETE = do_REQ

class ThreadingHTTPServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):
    pass


def start(port=default_port):
    log.info('Started')

    global use_port
    use_port = port

    HandlerClass = ProxyHandler
    ServerClass = ThreadingHTTPServer
    protocol = "HTTP/1.0"

    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    log.info("Serving HTTP on %s port %s ..." % (sa[0], sa[1]))
    while running:
        httpd.handle_request()
    log.info('Stopped')

def thread_start(port=default_port):
    import threading
    class ProxyThread(threading.Thread):
        def __init__(self, name='ListenThread'):
            threading.Thread.__init__(self, name=name)
        def run(self):
            start(port)
    thread = ProxyThread() 
    thread.start()
    return thread

def stop():
    global running
    running = 0
    log.info('Stopping')
    import urllib
    proxies = {'http': 'http://localhost:%s'%use_port}
    try:
        urllib.urlopen(STOPPING_URL, proxies=proxies)
    except:
        pass

def begin_catch(callback = None, filter = None, hittype = None):
    global respcallback, respfilter, HitType
    if callback:
        respcallback = callback
    if filter:
        respfilter = filter
    if hittype:
        HitType = hittype
    if not HitType:
        import Record
        HitType = Record.Hit

def end_catch():
    global respcallback, respfilter
    respfilter = EmptyFilter()
    respcallback = lambda x: False

def test():
    begin_catch(filter = DefaultContentFilter())
    start(default_port)

def test_thread():
    thread_start()
    begin_catch(filter = DefaultContentFilter())
    import time
    time.sleep(10)
    h = end_catch()

if __name__ == '__main__':
    test()

# vim:expandtab:shiftwidth=4
