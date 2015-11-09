# Superduper dockerfile to manage rails application!

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
    autoconf \
    automake \
    bison \
    gawk \
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
RUN gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
RUN curl -O https://raw.githubusercontent.com/rvm/rvm/master/binscripts/rvm-installer
RUN curl -O https://raw.githubusercontent.com/rvm/rvm/master/binscripts/rvm-installer.asc
RUN gpg --verify rvm-installer.asc && bash rvm-installer stable || echo ":("

RUN /bin/bash -l -c "\
    source /etc/profile.d/rvm.sh && \
    rvm install 2.2 && \
    rvm alias create default 2.2 && \
    gem install bundler rails rack uwsgi"

RUN rm rvm-installer*

## Runit
ADD scripts/runit/uwsgi /etc/service/uwsgi/run
RUN chmod +x /etc/service/uwsgi/run

# Config
ENV CONFIG Rails
