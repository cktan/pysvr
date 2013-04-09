Preemble
--------

Install pip and virtualenv.

    curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
    sudo python get-pip.py
    sudo pip install virtualenv```

Get the code.

    cd /o
    git clone https://github.com/cktan/pysvr.git
    cd /o/pysvr

Set up virtualenv.

    virtualenv env
    source env/bin/activate

Install Python Packages.

    pip install bottle psycopg2 boto statsd redis
    pip install http://projects.unbit.it/downloads/uwsgi-lts.tar.gz

Prepare to Run
--------------
The system stores log in /var/log/:appname/, pid files in /var/run/:appname/, and temp files in /var/run/:appname/. We need to create these directories with write credentials.

    sudo mkdir /var/{log,run,tmp}/pysvr
    sudo chown $USER /var/{log,run,tmp}/pysvr
    
Next, in preparation for deployment via Capistrano on a separate dir structure, we always link to the runtime dir via a symbolic link *current*.

    cd /o/pysvr
    ln -s runtime current

Give it a Spin
--------------
To start:

    cd /o/pysvr/current
    bash pysvr_ctl.sh restart

Here is some simple tests:

    curl http://localhost:8686/documents/
    curl http://localhost:8686/documents/20
    curl -X PUT http://localhost:8686/documents -d '{"_id": 123}'
    curl -X POST http://localhost:8686/documents/20 -d '{"name": “john wayne”}'
    curl -X DELETE http://localhost:8686/documents/20 
    
To look at the logs:

    tail -f /var/log/pysvr/app.log
    
To see the processes:

    ps -ef | grep nginx | grep pysvr
    ps -ef | grep uwsgi | grep pysvr
    ps -ef | grep plog | grep pysvr

