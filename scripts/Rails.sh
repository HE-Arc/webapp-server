#!/bin/sh

set -xe

cp /var/templates/rails/README.md /var/www/
cp /var/templates/rails/config/nginx.conf /var/www/config/nginx.conf
cp /var/templates/rails/config/puma.rb /var/www/config/puma.rb
cp -r /var/templates/rails/app /var/www/app

gem install bundler puma
cd /var/www/app
bundler install
