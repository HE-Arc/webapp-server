#!/bin/bash
set -ex
exec 2>&1
exec /usr/sbin/php-fpm7.0 --nodaemonize
