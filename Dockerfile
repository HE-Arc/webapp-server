# Superduper dockerfile to manage php application!

FROM jedisct1/phusion-baseimage-latest:latest
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22
EXPOSE 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

RUN apt-get update
RUN apt-get upgrade -y -q
RUN apt-get install -y -q \
    ack-grep \
    build-essential \
    curl \
    git \
    mariadb-client \
    nginx \
    nodejs \
    npm \
    php5-cli \
    php5-curl \
    php5-fpm \
    php5-imagick \
    php5-mcrypt \
    php5-mysql \
    php5-xdebug \
    pwgen \
    python3-pip \
    python3-software-properties \
    screen \
    sudo \
    tmux \
    toilet \
    unzip \
    vim \
    wget

RUN pip3 install \
    jinja2 \
    pymysql \
    requests

# Enable SSHD
RUN rm -f /etc/service/sshd/down
# Regenerate SSH host keys. baseimage-docker does not contain any, so you
# have to do that yourself. You may also comment out this instruction; the
# init system will auto-generate one during boot.
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

## Install the SSH keys of your choice.
ADD keys/yoan.pub /tmp/yoan.pub
#ADD keys/david.pub /tmp/david.pub
RUN cat /tmp/yoan.pub >> /root/.ssh/authorized_keys

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

## Nginx
RUN rm /etc/nginx/sites-enabled/default
RUN rm -r /var/www/html
# only one worker process and no daemonize
RUN sed -i 's/\(worker_processes\) .;/\1 1;\ndaemon off;/' /etc/nginx/nginx.conf

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
ADD scripts/runit/nginx /etc/service/nginx/run
RUN chmod +x /etc/service/nginx/run
ADD scripts/runit/nginx-log-forwarder /etc/service/nginx-log-forwarder/run
RUN chmod +x /etc/service/nginx-log-forwarder/run
ADD scripts/runit/php5-fpm /etc/service/php5-fpm/run
RUN chmod +x /etc/service/php5-fpm/run

#
# SUDO for any user
#
RUN echo '%users ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/users
RUN chmod 0440 /etc/sudoers.d/users

# Enable screen
RUN chmod 0777 /var/run/screen

# Composer / Laravel
ADD files/composer.phar $HOME/composer.phar
ADD files/composer $HOME/.composer

# Init.d
ADD files/templates $HOME/templates
ADD config/students.tsv $HOME/students.tsv
ADD scripts/30_setup.py /etc/my_init.d/30_setup.py
RUN chmod +x /etc/my_init.d/30_setup.py

# Expose VOLUME
VOLUME /var/www

# Config
ENV GROUPNAME unknown
