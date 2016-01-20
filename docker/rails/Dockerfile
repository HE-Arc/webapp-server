# Superduper dockerfile to manage rails application!

FROM greut/webapp-server:latest
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
        ruby2.2 \
        ruby2.2-dev \
        xvfb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/tmp/*

RUN echo "gem: --no-document" > /etc/gemrc
RUN update-alternatives --install /usr/bin/ruby ruby /usr/bin/ruby2.2 1 \
        --slave /usr/share/man/man1/ruby.1.gz ruby.1.gz /usr/share/man/man1/ruby2.2.1.gz \
        --slave /usr/bin/irb irb /usr/bin/irb2.2 \
        --slave /usr/bin/gem gem /usr/bin/gem2.2 \
        --slave /usr/bin/ri ri /usr/bin/ri2.2

## Runit
ADD scripts/runit/puma /etc/service/puma/run
RUN chmod +x /etc/service/puma/run

# Config
ENV CONFIG Rails
