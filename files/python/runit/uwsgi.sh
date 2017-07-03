#!/bin/sh

set -e

cd "/var/www/app"
exec 2>&1

ENV_FILE="/etc/container_environment"
UWSGI_INI="../config/uwsgi.ini"
RUNIT_USER=`stat -c %U $UWSGI_INI`
COMMAND="uwsgi --ini $UWSGI_INI"

exec chpst -u $RUNIT_USER -e $ENV_FILE $COMMAND
