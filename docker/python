FROM greut/webapp-server:latest
LABEL maintainer="Yoan Blanc <yoan@dosimple.ch>"


RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update -q -y \
 && apt-get install -q -y \
        libpcre3-dev \
        uwsgi \
        uwsgi-plugin-python3 \
        uwsgi-plugin-asyncio-python3 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /var/tmp/*

## Runit
COPY scripts/runit/uwsgi.sh /etc/service/uwsgi/run
RUN chmod +x /etc/service/uwsgi/run

# Develop
COPY files/templates /var/templates
COPY scripts/boot.sh /usr/local/bin/boot.sh
COPY scripts/setup.py /usr/local/bin/setup.py
RUN chmod +x /usr/local/bin/boot.sh \
 && chmod +x /usr/local/bin/setup.py


# Config
ENV CONFIG Python

# vim: ft=dockerfile:
