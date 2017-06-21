#!/bin/sh

set -xe

# regen SSH keys on each boot.
if [ 0 -eq `ls /etc/ssh/ssh_host_* | wc -l` ]
    then
    dpkg-reconfigure openssh-server
fi

# pre-setup
if [ ! -d /var/www/config ]
    then
    mkdir /var/www/config
    mkdir /var/www/logs

    # global config
    ${CONFIG}.sh

    username=poweruser

    uid=`id -u $username`
    gid=`id -g $username`

    # change the rights
    find /var/www -user root -exec chown -h $uid {} \;
    find /var/www -group root -exec chgrp -h $gid {} \;

    # create the users and finalize the setup.
    /usr/local/bin/setup.py

    # enable nginx
    ln -s /var/www/config/nginx.conf /etc/nginx/sites-enabled/default
fi

exec /usr/bin/runsvdir -P /etc/service
