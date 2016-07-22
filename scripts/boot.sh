#!/bin/sh

set -xe

# regen SSH keys on each boot
if [ 0 -eq `ls /etc/ssh/ssh_host_* | wc -l` ]; then
    dpkg-reconfigure openssh-server
fi

/usr/local/bin/setup.py

exec /usr/bin/runsvdir -P /etc/service
