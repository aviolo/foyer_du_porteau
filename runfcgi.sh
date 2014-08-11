#!/bin/bash
# To make this script start at boot:
# cp tests_displayer_init.sh /etc/init.d/tests_displayer
# chmod +x /etc/init.d/tests_displayer
# update-rc.d tests_displayer defaults 99 00

PROJ_NAME="Foyer du Porteau"
PROJ_USER="fdp"
PROJ_DIR="/home/$PROJ_USER/site"
PID_FILE="$PROJ_DIR/django.pid"
FCGI_HOST="127.0.0.1"
FCGI_PORT="3000"

# check arg
if [[ $1 != "stop" && $1 != "start" && $1 != "restart" ]]; then
    echo "Usage: $0 start|stop|restart"
    exit 1
fi

cd $PROJ_DIR

# stop
if [[ $1 = "stop" || $1 = "start" || $1 = "restart" ]]; then
    echo "Stopping $PROJ_NAME ... "
    killed=false
    if [ -f $PID_FILE ]; then
        PID=$(cat -- $PID_FILE)
        kill -9 $PID
        if [[ $? == 1 ]]; then
            killed=true
        fi
        rm -f -- $PID_FILE
    fi
    if [[ !killed ]]; then
        pkill -9 -f -- "$PROJ_DIR/manage.py runfcgi"
    fi
    echo "    [ OK ]"
fi

# start
if [[ $1 = "start" || $1 = "restart" ]]; then
    echo "Starting $PROJ_NAME ... "
    CMD_LINE="/bin/bash -c"
    if [[ $(whoami) != $PROJ_USER ]]; then
        CMD_LINE="sudo su $PROJ_USER -c"
    fi
    $CMD_LINE "python $PROJ_DIR/manage.py runfcgi host=$FCGI_HOST port=$FCGI_PORT pidfile=$PID_FILE method=prefork maxchildren=4 maxspare=2 minspare=2 daemonize=true"
    echo "    [ OK ]"
fi

echo "Done"
exit 0

