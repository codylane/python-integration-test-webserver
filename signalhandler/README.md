python-signalhandler
====================

Cool little library for trapping and handling signals and performing a custom action.  This code was created back in 2009 when I had a need to write a custom daemon in python.  The original daemon code was found here, http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/ and this signal handler code was used to processing IPC signals to inform the daemon code to perform special actions.

Example Code sighandler.py
==========================
```
import signal
import os
import sys
from SignalHandler import SignalHandler

def stop():
    print "Called the stop().... Exitting 0"
    sys.exit(0)

def abort():
    print "Called abort().... Exitting 1"
    sys.exit(1)

if __name__ == '__main__':
    # Create SignalHandler object
    sighandler = SignalHandler()

    # Now register a SIGTERM (kill -15) and callback
    # object when signal is trapped.
    sighandler.register( signal.SIGTERM, stop)

    # Register a SIGINT (kill -2) and callback
    # object when sign is trapped.
    # This is equivalent to CTRL-C
    sighandler.register( signal.SIGINT, abort )

    # Display the current registered signal events.
    # This is just for show and tell purposes.
    print "Implemented Signals: ", sighandler.getActions()

    while True:
        print "Waiting for signal.... Running pid: %s" %(os.getpid())
        signal.pause()
```
Example Usage From Code Above
=============================
```
$ ./sighandler.py &
[1] 5277
Implemented Signals:  (<Class:SigAction signal:15>, <Class:SigAction signal:2>)
Waiting for signal.... Running pid: 5277

$ kill 5277
Called the stop().... Exitting 0
$
```
