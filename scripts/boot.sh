#!/bin/sh

set -xe

# regen SSH keys on each boot.
if [ 0 -eq `ls /etc/ssh/ssh_host_* | wc -l` ]; then
    dpkg-reconfigure openssh-server
fi

# create the users and finalize the setup.
/usr/local/bin/setup.py

exec /usr/bin/runsvdir -P /etc/service
