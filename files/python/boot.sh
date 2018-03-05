#!/bin/sh

set -xe

cp /var/templates/python/README.md /var/www/
[ ! -f /var/www/config/nginx.conf ] && cp /var/templates/python/config/nginx.conf /var/www/config/nginx.conf
[ ! -f /var/www/config/uwsgi.ini ] && cp /var/templates/python/config/uwsgi.ini /var/www/config/uwsgi.ini

if [ ! -d /var/www/app ]
then
    cp -r /var/templates/python/app /var/www/app

    # configure python
    python3 -m venv /var/www/app/venv
    /var/www/app/venv/bin/pip --no-cache-dir install -U pip setuptools wheel
fi
