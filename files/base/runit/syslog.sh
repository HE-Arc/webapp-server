#!/bin/sh
set -xe

exec syslog-ng -F -p /var/run/syslog-ng.pid --no-caps
