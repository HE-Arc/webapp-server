#!/bin/sh

set -xe

username=poweruser

uid=`id -u $username`
gid=`id -g $username`

# change the rights
find /var/www -user root -exec chown -h $uid {} \;
find /var/www -group root -exec chgrp -h $gid {} \;

# regen SSH keys on each boot.
if [ 0 -eq `ls /etc/ssh/ssh_host_* | wc -l` ]; then
    dpkg-reconfigure openssh-server
fi

# create the users and finalize the setup.
/usr/local/bin/setup.py

exec /usr/bin/runsvdir -P /etc/service
