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
    libmagickwand-dev \
    libqt4-webkit \
    libqt4-dev \
    libv8-dev \
    libxml2-dev \
    libxslt1-dev \
    xvfb


# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Init.d
ENV CONFIG Rails
