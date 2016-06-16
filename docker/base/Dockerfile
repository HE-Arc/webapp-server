# Superduper dockerfile to manage web application!

FROM jedisct1/phusion-baseimage-latest:latest
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

# NodeSource special setup does the apt-get update already, even twice.
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get upgrade -q -y && \
    apt-get install -q -y \
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
        python3-pip \
        python3-virtualenv \
        pwgen \
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
        xfonts-75dpi && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
    locale-gen en_US && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=fr_CH.UTF-8 LC_MESSAGES=POSIX

# Python
RUN python3 -m pip install jinja2

# Install some npm global packages.
RUN npm install -g \
        bower \
        gulp \
        grunt-cli \
        webpack

# Clean up tmp when done.
RUN rm -rf /tmp/* /var/tmp/*

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
    sed -i 's/^\(http {\)/env MYSQL_USERNAME;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env MYSQL_PASSWORD;\n\n\1/' /etc/nginx/nginx.conf && \
    # Postgres
    sed -i 's/^\(http {\)/env POSTGRES_USERNAME;\n\1/' /etc/nginx/nginx.conf && \
    sed -i 's/^\(http {\)/env POSTGRES_PASSWORD;\n\n\1/' /etc/nginx/nginx.conf

# SSMTP
# mailhub configuration is done by 30_setup.py
RUN sed -i 's/#FromLineOverride=YES/FromLineOverride=YES/' /etc/ssmtp/ssmtp.conf

# LOGROTATE
RUN sed -i 's/^su root syslog/su root adm/' /etc/logrotate.conf
COPY files/templates/vhost.logrotate /etc/logrotate.d

#
# SUDO for any user
#
RUN echo '%users ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/users
RUN chmod 0440 /etc/sudoers.d/users

## Runit
COPY scripts/runit/nginx /etc/service/nginx/run
COPY scripts/runit/nginx-log-forwarder /etc/service/nginx-log-forwarder/run
COPY files/templates /var/templates
COPY scripts/30_setup.py /etc/my_init.d/30_setup.py
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
