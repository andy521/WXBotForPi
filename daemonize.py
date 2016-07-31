#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time


STDOUT = ""
STDERR = ""
UMASK = 0022
MAXFD = 1024

# The standard I/O file descriptors are redirected to /dev/null by default.
if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"

def createDaemon():
    global STDOUT
    global STDERR
    global UMASK
    global MAXFD

    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if pid > 0:
        os._exit(0) # 父进程退出

    os.setsid()

    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)

    if pid > 0:
        os._exit(0) # 第一子进程退出

    os.umask(UMASK)

    # close file descriptors
    import resource     # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD

    try:
        os.closerange(0, maxfd)
    except OSError:   # ERROR, fd wasn't open to begin with (ignored)
        pass

    if not STDOUT:
        STDOUT = REDIRECT_TO
    if not STDERR:
        STDERR = REDIRECT_TO

    os.open(REDIRECT_TO, os.O_RDWR) # stdin
    os.open(STDOUT, os.O_RDWR | os.O_CREAT)      # stdout
    os.open(STDERR, os.O_RDWR | os.O_CREAT)      # stderr
    return 0