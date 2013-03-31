F=/o/dataservice-config/current/my.env
if [ -r $F ]; then
    . $F
else
    echo cannot read $F
    exit 1
fi

if [ ${UID} == 0 ]; then
    echo Cannot start service as root user;
    exit 1;
fi

if [ ! -e /o/odeskdev-pysvr/current ]; then
    echo Missing dir /o/odeskdev-pysvr/current
fi

function fatal {
    echo '[FATAL]' $@
    exit 1
}

CUR=/o/odeskdev-pysvr/current
ETC=$CUR/etc
TMP=/var/tmp/pysvr

nginx -c $ETC/pysvr_nginx.conf 2> $TMP/nginx_error.log || fatal nginx failed to start
uwsgi --ini $ETC/pysvr_uwsgi.ini || fatal uwsgi failed to start

echo OK
