#!/bin/bash
PROJ_USER="fdp"
PROJ_DIR="/home/$PROJ_USER/fdp"

# get command to run
CMD="pull"
if [[ $1 = "status" ]]; then
    CMD="status"
else
    if [[ $1 != "" && $1 != "update" && $1 != "pull" ]]; then
        echo "Invalid argument given. Valid arguments are: update|status."
        exit 1
    fi
fi

cd $PROJ_DIR

# get command prompt
CMD_LINE="/bin/bash -c"
if [[ $(whoami) != $PROJ_USER ]]; then
    CMD_LINE="sudo su $PROJ_USER -c"
fi

# run command
echo "Running $CMD command ... "
$CMD_LINE "git $CMD"
if [ $? ]; then
    echo -e "    \033[92m[ OK ]\033[0m"
    website-uwsgi.sh restart
    exit $?
else
    echo -e "    \033[91m[ FAILED ]\033[0m"
    exit 1
fi
