import psycopg2, psycopg2.extras
import sys, os, time

### ------------------------------------------
class Error(Exception):
    '''Base class for exceptions in this module'''

### ------------------------------------------
class RuntimeError(Error):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

### ------------------------------------------
class ConfigError(RuntimeError):
    def __init__(self, msg):
        super(ConfigError, self).__init__(msg)

### ------------------------------------------
class Pool:
    tab = {}
    
    @staticmethod
    def put(dsn, dbconn):
        if dsn not in Pool.tab:
            Pool.tab[dsn] = []
        Pool.tab[dsn].append( (dbconn, time.time() + 60*10) )

    @staticmethod
    def get(dsn):
        while True:
            (c, xtime) = Pool.tab.get(dsn, [ (None, None) ]).pop(0)
            if not c:
                return psycopg2.connect(dsn)
            if xtime > time.time():
                return c
            c.close()
        
### ------------------------------------------
class DB:
    def __init__(self, dsn):
        self.__dsn = dsn
        self.__conn = None

    def __enter__(self):
        return self.open()

    def __exit__(self, type, value, tb):
        self.close()

    def open(self):
        if not self.__conn:
            self.__conn = Pool.get(self.__dsn)
        return self

    def close(self):
        c = self.__conn
        self.__conn = None
        if c:
            c.commit()
            Pool.put(self.__dsn, c)

    def query(self, sql, param):
        ok = False
        cur = self.__conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cur.execute(sql, param)
            out = cur.fetchall()
            ok = True
            return out
        finally:
            cur.close()
            if ok:
                self.__conn.commit()
            else:
                self.__conn.rollback()


### ------------------------------------------
def dsn(dbname, uname, host, port='5432'):
    def env(k, defval=''):
        r = os.environ.get(k, defval)
        if not r:
            raise ConfigError('env-var %s not set' % k)
        return r

    p = env('PG_PASSWORD_%s_%s' % (dbname.upper(), uname.upper()))
    return 'dbname=%s user=%s password=%s host=%s port=%s' % (dbname, uname, p, host, port)


### ------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.exit('Usage: %s uname dbname host port {sql|-}' % sys.argv[0])

    (uname, dbname, host, port, sql) = sys.argv[1:]
    if sql == '-':
        sql = sys.stdin.read()
        if not sql:
            sys.exit('Error: cannot read sql from stdin')

    d = dsn(dbname, uname, host, port)

    # this will create one connection
    with DB(d) as db:
        print db.query(sql, ())
        # this will create another connection
        with DB(d) as db:
            for i in db.query(sql, ()):
                print i

    # reuse one of the connections above
    with DB(d) as db:
        for i in db.query(sql, ()):
            print i
