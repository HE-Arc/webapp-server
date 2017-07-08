#!/bin/sh

set -xe

username=poweruser

# regen SSH keys / passwords on each boot.

if [ 0 -eq `ls /etc/ssh/ssh_host_* | wc -l` ]
then
    dpkg-reconfigure openssh-server

    # randomize the password
    echo $username:`pwgen 64 1` | chpasswd
fi


# Environment variables
export MYSQL_HOST=${MYSQL_HOST:-mysql}
export MYSQL_PORT=${MYSQL_PORT:-3306}
export POSTGRES_HOST=${POSTGRES_HOST:-postgres}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export REDIS_HOST=${REDIS_HOST:-redis}
export REDIS_PORT=${REDIS_PORT:-6379}
export SMTP_HOST=${SMTP_HOST:-smtp}
export SMTP_PORT=${SMTP_PORT:-1025}

# Rails
export SECRET_KEY_BASE=${SECRET_KEY_BASE:-`pwgen 128 1`}
# Django
export SECRET_KEY=${SECRET_KEY:-$SECRET_KEY_BASE}

mkdir -p /etc/container_environment

awk 'END { for (name in ENVIRON) {
    if (name != "PWD" && name != "USER" && name != "HOSTNAME" && name != "PATH" && name != "HOME")
      print ENVIRON[name] > "/etc/container_environment/"name
  }
}' < /dev/null

# pre-setup
mkdir -p /var/www/config
mkdir -p /var/www/logs

uid=`id -u $username`
gid=`id -g $username`

# change the rights
find /var/www -user root -exec chown -h $uid {} \;
find /var/www -group root -exec chgrp -h $gid {} \;

# global config
chpst -u $username sh /var/templates/${CONFIG}/boot.sh
# Postgres helper
chpst -u $username sh -c "echo $POSTGRES_HOST:$POSTGRES_PORT:$GROUPNAME:$GROUPNAME:$PASSWORD > /home/$username/.pgpass"
chmod 0600 /home/$username/.pgpass


# enable nginx
[ ! -f /etc/nginx/sites-enabled/default ] && ln -s /var/www/config/nginx.conf /etc/nginx/sites-enabled/default

# set ssh keys
touch /home/$username/.ssh/authorized_keys
for u in $SSH_KEYS
do
    curl https://api.github.com/users/$u/keys \
        | jq -r ".[]|.key+\" \"+(.id|tostring)+\"@$u\"" \
        | tee -a /home/$username/.ssh/authorized_keys
done


exec /usr/bin/runsvdir -P /etc/service
