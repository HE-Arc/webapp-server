# Superduper dockerfile to manage php application!

FROM greut/webapp-server:latest
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

ENV DEBIAN_FRONTEND=noninteractive

RUN sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E5267A6C && \
    add-apt-repository ppa:ondrej/php -y && \
    apt-get update -q && \
    apt-get update -q && \
    apt-get upgrade -q -y --allow-unauthenticated && \
    apt-get install -q -y --allow-unauthenticated \
        php-apcu \
        php7.0-cli \
        php7.0-curl \
        php7.0-intl \
        php7.0-fpm \
        php-imagick \
        php7.0-mcrypt \
        php-memcache \
        php-memcached \
        php7.0-mysql \
        php7.0-pgsql \
        php-redis \
        php-xdebug && \
    apt-get autoremove

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*

# PHP 7.0 FPM (fix)
RUN mkdir -p /run/php

# Enable mcrypt
RUN phpenmod mcrypt

## PHP ini
RUN sed -i 's/;\(date.timezone =\).*/\1 "Europe\/Zurich"/' /etc/php/7.0/fpm/php.ini
RUN sed -i 's/\(error_reporting =\).*/\1 E_ALL/' /etc/php/7.0/fpm/php.ini
RUN sed -i 's/\(display_errors =\).*/\1 On/' /etc/php/7.0/fpm/php.ini
RUN sed -i 's/;\(cgi.fix_pathinfo=\).*/\1 0/' /etc/php/7.0/fpm/php.ini

RUN sed -i 's/;\(date.timezone =\).*/\1 "Europe\/Zurich"/' /etc/php/7.0/cli/php.ini
RUN sed -i 's/\(error_reporting =\).*/\1 E_ALL/' /etc/php/7.0/cli/php.ini
RUN sed -i 's/\(display_errors =\).*/\1 On/' /etc/php/7.0/cli/php.ini
RUN sed -i 's/;\(cgi.fix_pathinfo=\).*/\1 0/' /etc/php/7.0/cli/php.ini

## Runit
ADD scripts/runit/php7.0-fpm /etc/service/php7.0-fpm/run
RUN chmod +x /etc/service/php7.0-fpm/run

# Composer (but no Laravel)
RUN curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer

# Config
ENV CONFIG Laravel
