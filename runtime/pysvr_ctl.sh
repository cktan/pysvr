# export PATH="...:$PATH";
source ../env/bin/activate

[ $UID != 0 ] || fatal cannot run as root user

CUR=/o/pysvr/current
ETC=$CUR/etc
TMP=/var/tmp/pysvr
RUN=/var/run/pysvr
LOG=/var/log/pysvr

function fatal { echo '[FATAL]' $@; exit 1;}

function warning { echo '[WARNING]' $@; }

F=/o/dataservice-config/current/my.env
[ -r $F ] && source $F || warning cannot read $F

function check {
    # check that the processes are running
    (ps -fp $(< $RUN/nginx.pid) | grep nginx) &>/dev/null || fatal nginx not running
    (ps -fp $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null || fatal uwsgi not running
    (ps -fp $(< $RUN/plog.pid) | grep plog) &>/dev/null || fatal plog not running
}

function start {
    [ -d $CUR ] || fatal missing dir $CUR - this is usually a symlink to the runtime dir.
    [ -d $ETC ] || fatal missing dir $ETC
    for i in $TMP $RUN $LOG; do 
	[ -d $i ] || fatal missing dir $i
	[ -w $i ] || fatal cannot write to dir $i
    done

    nginx -c $ETC/pysvr_nginx.conf 2>> $TMP/nginx_error.log || fatal nginx failed to start
    uwsgi --ini $ETC/pysvr_uwsgi.ini || fatal uwsgi failed to start
    python $CUR/lib/plog.py pysvr || fatal plog failed to start

    check
}

function stop {
    (ps -fp $(< $RUN/nginx.pid) | awk '/nginx/ {print $2}' | xargs kill -INT) &>/dev/null
    (ps -fp $(< $RUN/uwsgi.pid) | awk '/uwsgi/ {print $2}' | xargs kill -INT) &>/dev/null
    (ps -fp $(< $RUN/plog.pid) | awk '/plog/ {print $2}' | xargs kill -INT) &>/dev/null
    #pkill -F $RUN/nginx.pid nginx &>/dev/null
    #pkill -9 -F $RUN/uwsgi.pid uwsgi &>/dev/null

    sleep 1

    (ps -fp $(< $RUN/nginx.pid) | grep nginx) &>/dev/null && fatal nginx still running
    (ps -fp $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null && fatal uwsgi still running
    (ps -fp $(< $RUN/plog.pid) | grep plog) &>/dev/null && fatal plog still running
    #pgrep -F $RUN/nginx.pid nginx &>/dev/null && echo nginx still running
    #pgrep -F $RUN/uwsgi.pid uwsgi &>/dev/null && echo uwsgi still running
}


function reload {
    (ps -fp $(< $RUN/nginx.pid) | awk '/nginx/ {print $2}' | xargs kill -HUP) &>/dev/null
    (ps -fp $(< $RUN/uwsgi.pid) | awk '/uwsgi/ {print $2}' | xargs kill -HUP) &>/dev/null
    
    check
}


case "$1" in 
    start)      
	stop
	start
	;;
    stop)
	stop
	;;
    reload)
	reload
	;;
    *)
	echo "Usage: $0 {start|stop|reload}"
	exit 1
esac

echo OK
