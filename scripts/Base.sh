#!/bin/sh

set -xe

cp /var/templates/base/README.md /var/www/
cp /var/templates/base/config/nginx.conf /var/www/config/
cp -r /var/templates/base/public /var/www/
