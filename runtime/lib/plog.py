import sys, os, json
from socket import *
from time import gmtime
import conf

sock, dstaddr = None, None

def __init():
    global sock, dstaddr
    sock = socket(AF_INET, SOCK_DGRAM)
    port = conf.get('plog', 'port')
    dstaddr = ('localhost', int(port))

def __send(lev, msg):
    global sock, dstaddr
    t = gmtime()
    date = '%04d/%02d/%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    time = '%02d:%02d:%02d' % (t.tm_hour, t.tm_min, t.tm_sec)
    pkt = ' '.join( [date, time, lev, '-', msg] )
    sock.sendto(pkt, dstaddr)

def error(msg):
    __send('ERROR', msg)

def info(msg):
    __send('INFO ', msg)

def debug(msg):
    __send('DEBUG', msg)

def __daemonize():
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            os.wait()   # wait for second parent
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # decouple from parent environment
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            # print pid
            sys.exit(0)

    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    #change to data directory if needed
    if os.setsid() == -1:
        sys.exit('setsid failed')
    if os.umask(0) == -1:
        sys.exit('umask failed')

    import resource             # Resource usage information.
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024

    # Iterate through and close all file descriptors.
    sys.stdin.close()
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError: # ERROR, fd wasn't open to begin with (ignored)
            pass


def run():
    global sock, dstaddr
    sock.bind(dstaddr)
    dstdir = conf.get('plog', 'dir')
    print 'plog udp server: listening to port', dstaddr[1]
    print 'plog udp server: writing to', dstdir

    os.chdir(dstdir)

    def mkfname(tm):
        return 'app-%04d%02d%02d.log' % (tm.tm_year, tm.tm_mon, tm.tm_mday)

    ftime = gmtime()
    fp = open(mkfname(ftime), 'a+b')
    while 1:
        pkt, addr = sock.recvfrom(1024*8)
        if not pkt:
            break
        t = gmtime()
        if t.tm_mday != ftime.tm_mday:
            fp.close()
            ftime = t
            fp = open(mkfname(ftime), 'a+b')
        fp.write(pkt)
        fp.write('\n')

__init()
if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: %s pidfile' % sys.argv[0])

    pidpath = sys.argv[1]
    __daemonize()
    with open(pidpath, 'w') as fp:
        fp.write('%d\n' % os.getpid())
    __init()
    run()
