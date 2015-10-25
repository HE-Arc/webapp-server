# Superduper dockerfile to manage php application!

FROM greut/webapp-server:latest
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22
EXPOSE 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

RUN apt-get update -q
RUN apt-get upgrade -q -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y \
    php5-cli \
    php5-curl \
    php5-intl \
    php5-fpm \
    php5-imagick \
    php5-mcrypt \
    php5-memcache \
    php5-memcached \
    php5-mysql \
    php5-pgsql \
    php5-redis \
    php5-xdebug

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*

# Composer
RUN curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer

# Enable mcrypt
RUN php5enmod mcrypt

## PHP ini
RUN sed -i 's/;\(date.timezone =\).*/\1 "Europe\/Zurich"/' /etc/php5/fpm/php.ini
RUN sed -i 's/\(error_reporting =\).*/\1 E_ALL/' /etc/php5/fpm/php.ini
RUN sed -i 's/\(display_errors =\).*/\1 On/' /etc/php5/fpm/php.ini
RUN sed -i 's/;\(cgi.fix_pathinfo=\).*/\1 0/' /etc/php5/fpm/php.ini

RUN sed -i 's/;\(date.timezone =\).*/\1 "Europe\/Zurich"/' /etc/php5/cli/php.ini
RUN sed -i 's/\(error_reporting =\).*/\1 E_ALL/' /etc/php5/cli/php.ini
RUN sed -i 's/\(display_errors =\).*/\1 On/' /etc/php5/cli/php.ini
RUN sed -i 's/;\(cgi.fix_pathinfo=\).*/\1 0/' /etc/php5/cli/php.ini

## Runit
ADD scripts/runit/php5-fpm /etc/service/php5-fpm/run
RUN chmod +x /etc/service/php5-fpm/run

# Composer (but no Laravel)
RUN curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer

# Conf
ENV CONFIG Laravel
