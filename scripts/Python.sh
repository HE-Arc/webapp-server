#!/bin/sh

set -xe

cp /var/templates/python/config/nginx.conf /var/www/config/nginx.conf
cp /var/templates/python/config/uwsgi.ini /var/www/config/uwsgi.ini
cp -r /var/templates/python/app /var/www/app

# configure python
python3.6 -m venv /var/www/app/venv
/var/www/app/venv/bin/pip --no-cache-dir install -U pip
