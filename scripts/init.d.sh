#!/bin/bash

### BEGIN INIT INFO
# Provides:          fdp
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: fdp
# Description:       fdp management script
### END INIT INFO

PATH=/sbin:/usr/sbin:/bin:/usr/bin

# This script should be located in /etc/init.d/fdp
#   ln -s /home/fdp/fdp/scripts/init.d.sh /etc/init.d/fdp
# To make this script start at boot:
#   update-rc.d fdp defaults 96 00
# To remove it use:
#   update-rc.d -f fdp remove

if [[ $# < 1 ]]; then
    echo "Not enough arguments."
    exit 1
fi

/bin/su fdp -c "python3 /home/fdp/fdp/scripts/control.py $1"
