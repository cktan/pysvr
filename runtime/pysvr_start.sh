function fatal {
    echo '[FATAL]' $@
    exit 1
}

[ $UID != 0 ] || fatal cannot start service as root user

F=/o/dataservice-config/current/my.env
CUR=/o/pysvr/current
ETC=$CUR/etc
TMP=/var/tmp/pysvr
RUN=/var/run/pysvr
LOG=/var/log/pysvr

[ -r $F ] || fatal cannot read $F
[ -d $CUR ] || fatal missing dir $CUR
[ -d $ETC ] || fatal missing dir $ETC
for i in $TMP $RUN $LOG; do 
    [ -d $i ] || fatal missing dir $i
    [ -w $i ] || fatal cannot write to dir $i
done

. $F
nginx -c $ETC/pysvr_nginx.conf 2>> $TMP/nginx_error.log || fatal nginx failed to start
uwsgi --ini $ETC/pysvr_uwsgi.ini || fatal uwsgi failed to start

# check that the processes are running
(ps -p $(< $RUN/nginx.pid) | grep nginx) &>/dev/null || fatal nginx not running
(ps -p $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null || fatal uwsgi not running
echo OK
