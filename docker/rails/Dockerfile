# Superduper dockerfile to manage rails application!

FROM greut/webapp-server:base
MAINTAINER Yoan Blanc <yoan@dosimple.ch>

# Ports
EXPOSE 22 80

# Set correct environment variables.
ENV HOME /root

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update -q -y && \
    apt-get install -q -y \
        libgdbm-dev \
        libffi-dev \
        libncurses5-dev \
        libmagickwand-dev \
        libqt4-webkit \
        libqt4-dev \
        libreadline6-dev \
        libyaml-dev \
        libv8-dev \
        libxml2-dev \
        libxslt1-dev \
        xvfb

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/*

# RVM
RUN gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 && \
    curl -O https://raw.githubusercontent.com/rvm/rvm/master/binscripts/rvm-installer && \
    curl -O https://raw.githubusercontent.com/rvm/rvm/master/binscripts/rvm-installer.asc && \
    gpg --verify rvm-installer.asc && \
    bash rvm-installer stable && \
    /bin/bash -l -c "\
        source /etc/profile.d/rvm.sh && \
        rvm install 2.2 && \
        rvm alias create default 2.2 && \
        gem install bundler rails rack uwsgi" && \
    rm rvm-installer*

## Runit
ADD scripts/runit/uwsgi /etc/service/uwsgi/run
RUN chmod +x /etc/service/uwsgi/run

# Config
ENV CONFIG Rails
