# Superduper dockerfile to manage php application!

FROM greut/webapp-server:latest
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

RUN DEBIAN_FRONTEND=noninteractive \
    apt-key adv --keyserver keyserver.ubuntu.com --recv E5267A6C && \
    add-apt-repository ppa:ondrej/php -y && \
    apt-get update -q && \
    apt-get upgrade -q -y --allow-unauthenticated && \
    apt-get install -q -y --allow-unauthenticated \
        php-apcu \
        php7.0-cli \
        php7.0-curl \
        php7.0-intl \
        php7.0-fpm \
        php7.0-gd \
        php-imagick \
        php7.0-mbstring \
        php7.0-mcrypt \
        php-memcache \
        php-memcached \
        php-mongo \
        php-mongodb \
        php7.0-mysql \
        php7.0-pgsql \
        php7.0-sqlite3 \
        php-redis \
        php-xdebug && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/tmp/*

# Composer (but no Laravel)
RUN curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer

# PHP 7.0 FPM (fix)
RUN mkdir -p /run/php
RUN sed -i 's/^\(error_log = \).*$/\1syslog/' /etc/php/7.0/fpm/php-fpm.conf

# Enable mcrypt
RUN phpenmod mcrypt
# Disable xdebug for CLI (composer doesn't like it)
RUN phpdismod -s cli xdebug

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
COPY scripts/runit/php7.0-fpm /etc/service/php7.0-fpm/run
RUN chmod +x /etc/service/php7.0-fpm/run
#COPY files/templates /var/templates
#COPY scripts/30_setup.py /etc/my_init.d/30_setup.py
#RUN chmod +x /etc/my_init.d/30_setup.py

# Config
ENV CONFIG Laravel
