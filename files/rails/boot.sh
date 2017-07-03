#!/bin/sh

set -xe

cp /var/templates/rails/README.md /var/www/
cp /var/templates/rails/config/nginx.conf /var/www/config/nginx.conf
cp /var/templates/rails/config/puma.rb /var/www/config/puma.rb
cp -r /var/templates/rails/app /var/www/app

USER=`id -nu`
export GEM_HOME=/home/$USER/.gem/ruby/2.4.0
export PATH=$PATH:$GEM_HOME/bin

gem install bundler puma
cd /var/www/app
bundler install
