#!/bin/sh

set -xe

cp /var/templates/rails/README.md /var/www/
[ ! -f /var/www/config/nginx.conf ] && cp /var/templates/rails/config/nginx.conf /var/www/config/nginx.conf
[ ! -f /var/www/config/puma.rb ] && cp /var/templates/rails/config/puma.rb /var/www/config/puma.rb

if [ ! -d /var/www/app ]
then
    cp -r /var/templates/rails/app /var/www/app

    USER=`id -nu $username`
    RUBY_VERSION=`ruby --version | ruby -ne 'print /\b\d\.\d+/.match($_)'`
    export HOME=/home/$USER
    export GEM_HOME=/home/$USER/.gem/ruby/$RUBY_VERSION.0
    export PATH=$PATH:$GEM_HOME/bin

    gem install bundler puma
    cd /var/www/app
    bundler install
fi
