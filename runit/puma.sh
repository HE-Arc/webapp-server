#!/bin/sh

set -e

cd "/var/www/app"
exec 2>&1

export GEM_HOME="/var/www/.gem/ruby/2.4.0"
export PATH="$PATH:$GEM_HOME/bin"

ENV_FILE="/etc/container_environment"
PUMA_ENV="../config/puma.rb"
RUNIT_USER=`stat -c %U $PUMA_ENV`
COMMAND="puma --config $PUMA_ENV"

exec chpst -u $RUNIT_USER -e $ENV_FILE $COMMAND
