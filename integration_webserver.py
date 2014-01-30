#!/usr/bin/python

from __future__ import print_function
import os
import sys
import signal
import psutil
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from SocketServer import ForkingMixIn
from signalhandler.SignalHandler import SignalHandler
from daemon.daemon import Daemon

def get_execution_path():
    abs_path = os.path.abspath(sys.argv[0])
    root_dir = os.path.dirname(abs_path)
    return root_dir

LISTEN     = ''
PORT       = 48001
PIDFILE    = get_execution_path() + '/webserver.pid'
STDOUT_LOG = get_execution_path() + '/stdout.log'
STDERR_LOG = get_execution_path() + '/stderr.log'

class Endpoint(object):
    _path = None
    _callback = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, callback):
        self._callback = callback

    def __repr__(self):
        return 'Class:%s path:%s callback:%s' %(self.__class__.__name__, self._path, self._callback)

class MyHTTPServer(ForkingMixIn, HTTPServer):
    def __init__(self, host=LISTEN, port=PORT):
        HTTPServer.__init__(self, (host, port), MyHandler)
        self._endpoints = []
        self._sig_handler = SignalHandler()
        self.register_default_sig_handlers()

    def endpoints(self):
        return self._endpoints

    def register_default_sig_handlers(self):
        self._sig_handler.register(signal.SIGTERM, self.stop)
        self._sig_handler.register(signal.SIGINT,  self.stop)

    def run(self):
        try:
            self.serve_forever()
        except:
            self.server_close()
            self.shutdown()

    def stop(self):
        stop_server()

    def register_endpoint(self, path, return_val=None):
        if path not in self.endpoints():
            endpoint = Endpoint(path, return_val)
            self._endpoints.append(endpoint)

class DaemonizeMyHTTPServer(Daemon):
    def run(self, server):
        if isinstance(server, MyHTTPServer) is False:
            raise ValueError('server argument must be a MyHTTPServer instance, not %s=%s' %(type(server), server))
        self.daemonize()
        server.run()

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in self.server._endpoints:
            callback = server._endpoints.get('callback')
            self.send_valid_response(callback)
        else:
            self.send_invalid_response()

    def do_POST(self):
        pass

    def send_valid_response(self, callback):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if callback is None:
            self.wfile.write('20')
        else:
            self.wfile.write(callback())
        return

    def send_invalid_response(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        return

def start_server(daemonize=True):
    if daemonize:
        daemon = DaemonizeMyHTTPServer(
                pidfile = PIDFILE,
                stdin   = '/dev/null',
                stdout  = STDOUT_LOG,
                stderr  = STDERR_LOG
            )
        daemon.run(server)
    else:
        server.run()

def status_server():
    progname = sys.argv[0]
    for proc in psutil.process_iter():
        try:
            if progname in proc.cmdline and proc.pid != os.getpid():
                return proc.pid
        except:
            pass
    return None

def stop_server():
    pid = status_server()
    if pid is not None:
        os.kill(pid, signal.SIGTERM)
        return True
    return False

def usage():
    print('USAGE: %s [start|status|stop]')
    sys.exit(0)

if __name__ == '__main__':

    try:
        action = sys.argv[1]
    except:
        usage()

    if action == 'start':
        server = MyHTTPServer(LISTEN, PORT)
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=MaxPoolSize', 55)
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=MinPoolSize', 50)
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=NumBusyConnections')
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=NumIdleConnections')
        start_server()
    elif action == 'status':
        pid = status_server()
        if pid is not None:
            print('server running on port %s, pid %s' %(PORT, pid))
            sys.exit(0)
        else:
            print('server is not running.')
            sys.exit(2)
    elif action == 'stop':
        if stop_server() is False:
            print('server is not running, nothing to stop')
            sys.exit(1)
        else:
            print('stopped server')
        sys.exit(0)
    else:
        usage()
# if we get here just exit 0
sys.exit(0)
