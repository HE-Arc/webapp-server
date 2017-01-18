#!/bin/bash
set -ex
exec 2>&1

ENV_FILE="/etc/container_environment"
COMMAND="/usr/sbin/php-fpm --nodaemonize"

exec chpst -e $ENV_FILE $COMMAND
