#!/bin/sh

set -xe

cp /var/templates/laravel/README.md /var/www/
cp /var/templates/laravel/config/nginx.conf /var/www/config/nginx.conf
cp /var/templates/laravel/config/php-fpm.conf /var/www/config/php-fpm.conf
cp -r /var/templates/laravel/app /var/www/app


mv /etc/php/7.1/fpm/pool.d/www.conf /etc/php/7.1/fpm/pool.d/www.conf.old
ln -s /var/www/config/php-fpm.conf /etc/php/7.1/fpm/pool.d/www.conf
