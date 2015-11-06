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

# https://www.phusionpassenger.com/library/install/nginx/install/oss/wily/
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 \
    --recv-keys 561F9B9CAC40B2F7

RUN echo deb https://oss-binaries.phusionpassenger.com/apt/passenger wily main \
    > /etc/apt/sources.list.d/passenger.list

RUN apt-get update -q
RUN apt-get upgrade -q -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y \
    -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" \
    libmagickwand-dev \
    libqt4-webkit \
    libqt4-dev \
    libv8-dev \
    libxml2-dev \
    libxslt1-dev \
    nginx-extras # we must reinstall/upgrade nginx-extras with passenger \
    passenger \
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
    gem install bundler rails rack passenger"

RUN rm rvm-installer*

# Nginx
RUN sed -i 's/^\(http {\)/\1\npassenger_ruby \/usr\/bin\/passenger_free_ruby;\n/' /etc/nginx/nginx.conf
RUN sed -i 's/^\(http {\)/\1\npassenger_root \/usr\/lib\/ruby\/vendor_ruby\/phusion_passenger\/locations.ini;/' /etc/nginx/nginx.conf

# Config
ENV CONFIG Rails
