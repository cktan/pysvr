import sys, os
from socket import *
from time import gmtime
import conf

sock, dstaddr = None, None

def init():
    global sock, dstaddr
    sock = socket(AF_INET, SOCK_DGRAM)
    port = conf.get('plog', 'port')
    dstaddr = ('localhost', int(port))

def __write(lev, msg):
    global sock, dstaddr
    t = gmtime()
    date = '%02d/%02d/%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    time = '%02d:%02d:%02d' % (t.tm_hour, t.tm_min, t.tm_sec)
    pkt = ' '.join( [date, time, lev, ' - ', msg] )
    sock.sendto(pkt, dstaddr)

def error(msg):
    __write('ERROR', msg)

def info(msg):
    __write('INFO ', msg)

def debug(msg):
    __write('DEBUG', msg)

def run():
    global sock, dstaddr
    sock.bind(dstaddr)
    while 1:
        pkt, addr = sock.recvfrom(1024*8)
        if not pkt:
            break
        print pkt

init()
if __name__ == '__main__':
    run()
