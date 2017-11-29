#!/bin/sh

set -xe

cp /var/templates/base/README.md /var/www/
[ ! -f /var/www/config/nginx.conf ] && cp /var/templates/base/config/nginx.conf /var/www/config/ || echo ":-)"
[ ! -d /var/www/public ] && cp -r /var/templates/base/public /var/www/ || echo ":-)"
