# Superduper dockerfile to manage web application!

FROM jedisct1/phusion-baseimage-latest:latest
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# NodeSource special setup (does the apt-get update already, twice)
RUN curl -sL https://deb.nodesource.com/setup_5.x | bash -

RUN apt-get upgrade -q -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y \
    ack-grep \
    acl \
    apt-transport-https \
    build-essential \
    ca-certificates \
    cowsay \
    curl \
    fortunes \
    fortunes-fr \
    fontconfig \
    git \
    libcurl4-gnutls-dev \
    libmysqlclient-dev \
    libpq-dev \
    libsqlite3-dev \
    libxext6 \
    libxrender1 \
    lsof \
    man \
    mysql-client \
    mercurial \
    nano \
    nginx-extras \
    nodejs \
    postgresql-client \
    pwgen \
    python3-pip \
    python3-jinja2 \
    screen \
    sqlite3 \
    software-properties-common \
    ssmtp \
    subversion \
    sudo \
    tmux \
    toilet \
    unzip \
    vim \
    wget \
    xfonts-base \
    xfonts-75dpi

# wkhtmltopdf/wkhtmltoimage
RUN wget -nv http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb -O /tmp/wkhtmltox.deb
RUN dpkg -i /tmp/wkhtmltox.deb

# Locale
RUN locale-gen fr_CH && \
    locale-gen fr_CH.UTF-8 && \
    locale-gen de_CH && \
    locale-gen de_CH.UTF-8 && \
    locale-gen it_CH && \
    locale-gen it_CH.UTF-8 && \
    update-locale LANG=fr_CH.UTF-8 LC_MESSAGES=POSIX

# Update npm
RUN npm install -g \
        bower \
        gulp \
        grunt-cli \
        webpack \
        yo

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Vundle
RUN git clone https://github.com/VundleVim/Vundle.vim.git /var/Vundle.vim

# Enable SSHD
RUN rm -f /etc/service/sshd/down
# Regenerate SSH host keys. baseimage-docker does not contain any, so you
# have to do that yourself. You may also comment out this instruction; the
# init system will auto-generate one during boot.
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh

# Enable screen
RUN chmod 0775 /var/run/screen

## Nginx
RUN rm /etc/nginx/sites-enabled/default && \
    rm -r /var/www/html && \
    # auto worker processes and no daemonize (for my_init.d)
    sed -i 's/\(worker_processes\) .*;/\1 auto;\ndaemon off;/' /etc/nginx/nginx.conf && \
    # allow environment variables to be read by nginx confs
    # MySQL
    sed -i 's/^\(http {\)/env MYSQL_PORT_3306_TCP_ADDR;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env MYSQL_PORT_3306_TCP_PORT;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env MYSQL_USERNAME;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env MYSQL_PASSWORD;\n\n\1/' /etc/nginx/nginx.conf && \
    # Postgres
    sed -i 's/^\(http {\)/env POSTGRES_PORT_5432_TCP_ADDR;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env POSTGRES_PORT_5432_TCP_PORT;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env POSTGRES_USERNAME;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env POSTGRES_PASSWORD;\n\n\1/' /etc/nginx/nginx.conf && \
    # Memcached
    sed -i 's/^\(http {\)/env MEMCACHED_PORT_11211_TCP_ADDR;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env MEMCACHED_PORT_11211_TCP_PORT;\n\n\1/' /etc/nginx/nginx.conf && \
    # Redis
    sed -i 's/^\(http {\)/env REDIS_PORT_6379_TCP_ADDR;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env REDIS_PORT_6379_TCP_PORT;\n\n\1/' /etc/nginx/nginx.conf

# SSMTP
RUN sed -i 's/mailhub=mail/mailhub=mail:1025/' /etc/ssmtp/ssmtp.conf
RUN sed -i 's/#FromLineOverride=YES/FromLineOverride=YES/' /etc/ssmtp/ssmtp.conf

# LOGROTATE
RUN sed -i 's/^su root syslog/su root adm/' /etc/logrotate.conf
ADD files/templates/vhost.logrotate /etc/logrotate.d

#
# SUDO for any user
#
RUN echo '%users ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/users
RUN chmod 0440 /etc/sudoers.d/users

## Runit
ADD scripts/runit/nginx /etc/service/nginx/run
ADD scripts/runit/nginx-log-forwarder /etc/service/nginx-log-forwarder/run
ADD scripts/30_setup.py /etc/my_init.d/30_setup.py
RUN chmod +x /etc/service/nginx/run && \
    chmod +x /etc/service/nginx-log-forwarder/run && \
    chmod +x /etc/my_init.d/30_setup.py

# Expose VOLUME
VOLUME /var/templates \
    /root/config \
    /var/www

# Config
ENV GROUPNAME unknown
ENV CONFIG Base
