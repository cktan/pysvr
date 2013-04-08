import dbi, redis, json
import sys, os

### ------------------------------------------
class QCache:

    ### ------------------------------------------
    def __init__(self, rds, dsn):
        self.__rconn = rds
        self.__dsn = dsn

    ### ------------------------------------------
    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        self.__rconn = None

    ### ------------------------------------------
    def invalidate(self, qname, qkey):
        self.__rconn.delete(qname + ':' + qkey)
        
    ### ------------------------------------------
    def run10(self, qname, sql, qkeys, tmout):
        notfound = []
        out = {}
        
        if tmout <= 0:
            tmout = 0
            notfound = qkeys[:]
        else:
            # check cache
            for k in qkeys:
                r = self.__rconn.get(qname + ':' + k)
                if r:
                    r = json.loads(r)
                    r['_mc'] = 1
                    out[k] = r
                else:
                    notfound.append(k)

        if notfound:
            # pack it up to multiple of 10
            while len(notfound) % 10 != 0:
                notfound += [None]
            # split into list of list, each with 10 keys
            keychunk = [notfound[i:i+10] for i in xrange(0, len(notfound), 10)]
            with dbi.DB(self.__dsn) as db:
                for k10 in keychunk:
                    # run the query with 10 keys at a time
                    for r in db.query(sql, k10):
                        r['_mc'] = 0
                        k = r['_qkey']
                        out[k] = r
                        # put in cache
                        if tmout:
                            self.__rconn.setex(qname + ':' + k, tmout, json.dumps(r))
        return out


    ### ------------------------------------------
    def run1(self, qname, sql, qkey, tmout):

        if not isinstance(qkey, list) and not isinstance(qkey, tuple):
            qkey = (qkey,)
        
        if tmout <= 0:
            tmout = 0
        else:
            # check cache
            if len(qkey) == 1:
                r = self.__rconn.get(qname + ':' + qkey[0])
            else:
                r = self.__rconn.hget(qname + ':' + qkey[0], repr(qkey[1:]))

            # cache hit?
            if r:
                r = json.loads(r)
                r['_mc'] = 1
                return r

        # cache miss. run query.
        with dbi.DB(self.__dsn) as db:
            # note: this loop will only run once
            for r in db.query(sql, qkey):
                r['_mc'] = 0
                # put in cache
                if tmout:
                    if len(qkey) == 1:
                        self.__rconn.setex(qname + ':' + qkey[0], tmout, json.dumps(r))
                    else:
                        self.__rconn.hset(qname + ':' + qkey[0], repr(qkey[1:]), json.dumps(r))
                        self.__rconn.expire(qname + ':' + qkey[0], tmout)
                    
                return r

        return None


### ------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.exit('Usage: %s uname dbname dbhost dbport rhost rport' % sys.argv[0])

    (uname, dbname, host, port, rhost, rport) = sys.argv[1:]

    rds = redis.StrictRedis(rhost, int(rport))
    dsn = dbi.dsn(dbname, uname, host, port)
    qc = QCache(rds, dsn)

    def test_qrun1():
        qc.invalidate('myquery', 'pg_catalog')
        r = qc.run1('myquery',
                    'select * from pg_tables where schemaname=%s and tablename=%s',
                    ('pg_catalog', 'pg_class'), 60)
        assert r['_mc'] == 0

        r = qc.run1('myquery',
                    'select * from pg_tables where schemaname=%s and tablename=%s',
                    ('pg_catalog', 'pg_type'), 60)
        assert r['_mc'] == 0

        r = qc.run1('myquery',
                    'select * from pg_tables where schemaname=%s and tablename=%s',
                    ('pg_catalog', 'pg_class'), 60)
        assert r['_mc'] == 1

        r = qc.run1('myquery',
                    'select * from pg_tables where schemaname=%s and tablename=%s',
                    ('pg_catalog', 'pg_type'), 60)
        assert r['_mc'] == 1

    def test_qrun10():
        qc.invalidate('anotherquery', 'pg_class')
        qc.invalidate('anotherquery', 'pg_type')
        r = qc.run10('anotherquery',
                     '''select tablename as _qkey, * from pg_tables
                        where schemaname='pg_catalog'
                        and tablename in (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                     ('pg_class', 'pg_type'), 60)
        assert r['pg_class']['_mc'] == 0
        assert r['pg_type']['_mc'] == 0

        r = qc.run10('anotherquery',
                     '''select tablename as _qkey, * from pg_tables
                        where schemaname='pg_catalog'
                        and tablename in (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                     ('pg_class', 'pg_type', 'pg_am'), 60)
        assert r['pg_class']['_mc'] == 1
        assert r['pg_type']['_mc'] == 1
        assert r['pg_am']['_mc'] == 0

        r = qc.run10('anotherquery',
                     '''select tablename as _qkey, * from pg_tables
                        where schemaname='pg_catalog'
                        and tablename in (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                     ('pg_class', 'pg_type', 'pg_am'), 60)
        assert r['pg_class']['_mc'] == 1
        assert r['pg_type']['_mc'] == 1
        assert r['pg_am']['_mc'] == 1

    
    test_qrun1()
    test_qrun1()
    test_qrun10()
