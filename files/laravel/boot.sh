#!/bin/sh

set -xe

cp /var/templates/laravel/README.md /var/www/
[ ! -f /var/www/config/nginx.conf ] && cp /var/templates/laravel/config/nginx.conf /var/www/config/nginx.conf
[ ! -f /var/www/config/php-fpm.conf ] && cp /var/templates/laravel/config/php-fpm.conf /var/www/config/php-fpm.conf
[ ! -f /var/www/app ] && cp -r /var/templates/laravel/app /var/www/app


if [ ! -L /etc/php/7.2/fpm/pool.d/www.conf ]
then
    sudo mv /etc/php/7.2/fpm/pool.d/www.conf /etc/php/7.2/fpm/pool.d/www.conf.old
    sudo ln -s /var/www/config/php-fpm.conf /etc/php/7.2/fpm/pool.d/www.conf
fi
