F=/o/dataservice-config/current/my.env
CUR=/o/pysvr/current
ETC=$CUR/etc
TMP=/var/tmp/pysvr
RUN=/var/run/pysvr
LOG=/var/log/pysvr

function fatal {
    echo '[FATAL]' $@
    exit 1
}


[ $UID != 0 ] || fatal cannot run as root user
#[ -r $F ] || fatal cannot read $F
#. $F

function start {
    [ -d $CUR ] || fatal missing dir $CUR
    [ -d $ETC ] || fatal missing dir $ETC
    for i in $TMP $RUN $LOG; do 
	[ -d $i ] || fatal missing dir $i
	[ -w $i ] || fatal cannot write to dir $i
    done

    nginx -c $ETC/pysvr_nginx.conf 2>> $TMP/nginx_error.log || fatal nginx failed to start
    uwsgi --ini $ETC/pysvr_uwsgi.ini || fatal uwsgi failed to start

    # check that the processes are running
    (ps -p $(< $RUN/nginx.pid) | grep nginx) &>/dev/null || fatal nginx not running
    (ps -p $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null || fatal uwsgi not running
}

function stop {
    (ps -p $(< $RUN/nginx.pid) | awk '/nginx/ {print $1}' | xargs kill -INT) &>/dev/null
    (ps -p $(< $RUN/uwsgi.pid) | awk '/uwsgi/ {print $1}' | xargs kill -INT) &>/dev/null
    #pkill -F $RUN/nginx.pid nginx &>/dev/null
    #pkill -9 -F $RUN/uwsgi.pid uwsgi &>/dev/null

    sleep 1

    (ps -p $(< $RUN/nginx.pid) | grep nginx) &>/dev/null && fatal nginx still running
    (ps -p $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null && fatal uwsgi still running
    #pgrep -F $RUN/nginx.pid nginx &>/dev/null && echo 'NGINX still running'
    #pgrep -F $RUN/uwsgi.pid uwsgi &>/dev/null && echo 'UWSGI still running'
}


function reload {
    (ps -p $(< $RUN/nginx.pid) | awk '/nginx/ {print $1}' | xargs kill -HUP) &>/dev/null
    (ps -p $(< $RUN/uwsgi.pid) | awk '/uwsgi/ {print $1}' | xargs kill -HUP) &>/dev/null
    
    (ps -p $(< $RUN/nginx.pid) | grep nginx) &>/dev/null || fatal nginx not running
    (ps -p $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null || fatal uwsgi not running
}


case "$1" in 
    start) 
	start
	;;
    stop)
	stop
	;;
    reload)
	reload
	;;
    restart)
	stop
	start
	;;
    *)
	echo "Usage: $0 {start|stop|restart|reload}"
	exit 1
esac

echo OK
