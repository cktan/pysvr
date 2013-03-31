RUN=/var/run/pysvr

pkill -F $RUN/nginx.pid nginx &>/dev/null
pkill -9 -F $RUN/uwsgi.pid uwsgi &>/dev/null

sleep 1

pgrep -F $RUN/nginx.pid nginx &>/dev/null && echo 'NGINX still running'
pgrep -F $RUN/uwsgi.pid uwsgi &>/dev/null && echo 'UWSGI still running'

exit 0

