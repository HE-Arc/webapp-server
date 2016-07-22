#!/bin/sh

set -xe

/usr/local/bin/setup.py

exec /usr/bin/runsvdir -P /etc/service
