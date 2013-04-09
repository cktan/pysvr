from ConfigParser import ConfigParser
import os

cfg = None

def __load():
    global cfg
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, '..', 'etc', 'app.ini')
    cfg = ConfigParser()
    cfg.read(path)

def get(section, option, val=''):
    r = cfg.get(section, option)
    if r != None:
	return r
    return val

__load()
