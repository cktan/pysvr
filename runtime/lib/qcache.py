import dbi, redis, md5

class QCache:

    def __init__(self, rhost, rport=6379):
        self.__rconn = redis.StrictRedis(rhost)

    def invalidate(qname, qkey):
        self.__rconn.delete(qname + ':' + qkey)
        
    def run10(dsn, qname, sql, qkeys, tmout):
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
            with dbi.DB(dsn) as db:
                for k10 in keychunk:
                    # run the query with 10 keys at a time
                    for r in dbi.query(dbconn, sql, k10):
                        r['_mc'] = 0
                        k = r['_qkey']
                        out[k] = r
                        # put in cache
                        if tmout:
                            self.__rconn.setex(qname + ':' + k, tmout, r)
        return out


    def run1(dsn, qname, sql, qkey, tmout):
        if not isintance(qkey, list) and not isinstance(qkey, tuple):
            qkey = (qkey,)
        
        if tmout <= 0:
            tmout = 0
        else:
            # check cache
            if len(qkey) == 1:
                r = self.__rconn.get(qname + ':' + qkey[0])
            else:
                r = self.__rconn.hget(qname + ':' + qkey[0], repr(qkey[1:]))
            if r:
                r['_mc'] = 1
                return r

        with dbi.DB(dsn) as db:
            res = db.query(dbconn, sql, qkey)
            if res and res[0]:
                r = res[0]
                r['_mc'] = 0
                if tmout:
                    if len(qkey) == 1:
                        self.__rconn.setex(qname + qkey[0], tmout, r)
                    else:
                        self.__rconn.hset(qname + qkey[0], repr(qkey[1:]), r)
                        self.__rconn.expire(qname + qkey[0], tmout)
                    
        return r
