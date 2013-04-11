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

Install python packages.

    pip install bottle psycopg2 boto statsd redis
    pip install http://projects.unbit.it/downloads/uwsgi-lts.tar.gz

Prepare to Run
--------------
The system stores log in /var/log/:appname/, pid files in /var/run/:appname/, and temp files in /var/run/:appname/. We need to create these directories with write credentials.

    sudo mkdir /var/{log,run,tmp}/pysvr
    sudo chown $USER /var/{log,run,tmp}/pysvr
    
Next, in preparation for deployment via Capistrano on a separate directory structure, we always link to the runtime directory via a symbolic link: *current*.

    cd /o/pysvr
    ln -s runtime current

Give it a Spin
--------------
If you are not in the virtual environment, activate it as follows:

    cd /o/pysvr
    source env/bin/activate

To start:

    cd /o/pysvr/current
    bash pysvr_ctl.sh restart

Here are some simple tests:

    curl http://localhost:8686/dogs/
    curl http://localhost:8686/dogs/Bo
    curl -X POST http://localhost:8686/dogs -d '{"name": "Bo"}'
    curl -X PUT http://localhost:8686/dogs/Bo -d '{"name": "Bo", "color": "tricolor"}'
    curl -X DELETE http://localhost:8686/dogs/Bo 
    
To look at the logs:

    ls /var/log/pysvr
    tail -f /var/log/pysvr/app.log
    
To see the processes:

    ps -ef | grep nginx | grep pysvr
    ps -ef | grep uwsgi | grep pysvr
    ps -ef | grep plog | grep pysvr

