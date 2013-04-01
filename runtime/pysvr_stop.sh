RUN=/var/run/pysvr

(ps -p $(< $RUN/nginx.pid) | grep nginx | xargs kill) &>/dev/null
(ps -p $(< $RUN/uwsgi.pid) | grep uwsgi | xargs kill -9) &>/dev/null
#pkill -F $RUN/nginx.pid nginx &>/dev/null
#pkill -9 -F $RUN/uwsgi.pid uwsgi &>/dev/null

sleep 1

(ps -p $(< $RUN/nginx.pid) | grep nginx) &>/dev/null && echo NGINX still running
(ps -p $(< $RUN/uwsgi.pid) | grep uwsgi) &>/dev/null && echo UWSGI still running
#pgrep -F $RUN/nginx.pid nginx &>/dev/null && echo 'NGINX still running'
#pgrep -F $RUN/uwsgi.pid uwsgi &>/dev/null && echo 'UWSGI still running'

exit 0

