#!/bin/bash
PROJ_NAME="fdp"
PROJ_USER="fdp"
PROJ_DIR="/home/$PROJ_USER/fdp"
WSGI_INI="$PROJ_DIR/scripts/uwsgi.ini"
PID_FILE="$PROJ_DIR/uwsgi.pid"

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
        if kill -9 $PID; then
            killed=true
        fi
        rm -f -- $PID_FILE
    fi
    if [[ !killed ]]; then
        pkill -9 -f -- "uwsgi --ini $WSGI_INI"
    fi
    echo -e "    \033[92m[ OK ]\033[0m"
fi

# start
if [[ $1 = "start" || $1 = "restart" ]]; then
    echo "Starting $PROJ_NAME ... "
    CMD_LINE="/bin/bash -c"
    if [[ $(whoami) != $PROJ_USER ]]; then
        CMD_LINE="sudo su $PROJ_USER -c"
    fi
    $CMD_LINE "uwsgi --ini $WSGI_INI"
    if [ $? ]; then
        echo -e "    \033[92m[ OK ]\033[0m"
    else
        echo -e "    \033[91m[ FAILED ]\033[0m"
    fi
fi
