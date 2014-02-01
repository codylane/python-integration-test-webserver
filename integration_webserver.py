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
import random

def get_execution_path():
    abs_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(abs_path)
    return root_dir

LISTEN     = '0.0.0.0'
PORT       = 48000
PIDFILE    = get_execution_path() + '/webserver.pid'
STDOUT_LOG = get_execution_path() + '/stdout.log'
STDERR_LOG = get_execution_path() + '/stderr.log'

class Endpoint(object):
    def __init__(self, path, value=None, callback=None):
        self.path = path
        self.value = value
        self.callback = callback

    def __repr__(self):
        tostring = 'Class=%s' %(self.__class__.__name__)
        for key, value in self.__dict__.items():
            tostring += " %s=%s" %(key, value)
        return 'Class=%s path=%s value=%s callback=%s' \
                %(self.__class__.__name__, \
                  self.path, self.value, self.callback)

class MyHTTPServer(HTTPServer):
    def __init__(self, host=LISTEN, port=PORT):
        HTTPServer.__init__(self, (host, port), MyHandler)
        self._endpoints = {}
        self._sig_handler = SignalHandler()
        self.register_default_sig_handlers()

    def endpoints(self):
        return self._endpoints

    def register_default_sig_handlers(self):
        self._sig_handler.register(signal.SIGTERM, self.stop)
        self._sig_handler.register(signal.SIGINT,  self.stop)
        self._sig_handler.register(signal.SIGUSR1, self.list_endpoints)

    def run(self):
        try:
            self.serve_forever()
        except Exception as e:
            self.server_close()
            self.shutdown()

    def list_endpoints(self):
        for endpoint in self.endpoints():
            print('listing endpoint: %s' %(endpoint))
        self.run()

    def stop(self):
        stop_server()

    def register_endpoint(self, path, return_val=None, callback=None):
        if path not in self.endpoints():
            endpoint = Endpoint(path, return_val, callback)
            self._endpoints[path] = endpoint

class DaemonizeMyHTTPServer(Daemon):
    def run(self, server):
        if isinstance(server, MyHTTPServer) is False:
            raise ValueError('server argument must be a MyHTTPServer instance, not %s=%s' %(type(server), server))
        self.daemonize()
        server.run()

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        endpoints =  self.server.endpoints()
        if self.path in endpoints:
            callback = endpoints.get(self.path).callback
            self.send_valid_response(callback)
        else:
            self.send_invalid_response()

    def do_POST(self):
        pass

    def send_valid_response(self, callback):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        print('callback %s' %(callback))
        if callback is None:
            self.wfile.write('20')
        elif callable(callback):
            self.wfile.write(callback())
        else:
            self.wfile.write(callback)
        return

    def send_invalid_response(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
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

def list_endpoints():
    pid = status_server()
    if pid:
        os.kill(pid, signal.SIGUSR1)
        return True
    return False

def usage():
    print('USAGE: %s [start|status|endpoints|stop]')
    sys.exit(0)

def random_busy():
    return random.randint(1,40)

def random_idle():
    return random.randint(41,55)

if __name__ == '__main__':
    if not sys.argv[1:]:
        usage()
    action = sys.argv[1]

    if action == 'start':
        server = MyHTTPServer(LISTEN, PORT)
        print('starting up server http://%s:%s' %(LISTEN, PORT))
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=MaxPoolSize', 55)
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=MinPoolSize', 50)
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=NumBusyConnections', random_busy)
        server.register_endpoint('/twiddle/get.op?objectName=bean:name=datasource&attributeName=NumIdleConnections', random_idle) 
        start_server()
    elif action == 'status':
        pid = status_server()
        if pid:
            print('server running on port %s, pid %s' %(PORT, pid))
            sys.exit(0)
        else:
            print('server is not running.')
            sys.exit(2)
    elif action == 'endpoints':
        if list_endpoints():
            print('check your stdout.log')
        else:
            print('unable to list endpoints, server not runnin?')
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
