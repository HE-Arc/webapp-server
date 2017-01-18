#!/bin/sh

set -e

exec 2>&1

DIR="/var/www/iruby"
ENV_FILE="/etc/container_environment"
cd $DIR
RUNIT_USER=`stat -c %U Gemfile`

exec chpst -u $RUNIT_USER -e $ENV_FILE $DIR/.run.sh
