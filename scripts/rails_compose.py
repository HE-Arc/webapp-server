#!/usr/bin/env python3
"""
Rails Compose
-------------

Create the docker-compose YAML file for the users and CSV for the database.
"""

import csv
import sys

from collections import namedtuple
from jinja2 import Template
from passgen import passgen

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.1.0"

User = namedtuple(
    "User", "machine hostname github groupname password ssh http jupyter")
StudentRecord = namedtuple("StudentRecord",
                           "lastname, firstname, email, classname, github, "
                           "image1, team1, image2, team2, comment, week")

nginx = Template("""\
{%- for user in users %}
server {
    listen 80;
    listen [::]:80;

    server_name {{ user.hostname }}.srvzct-52.he-arc.ch {{ user.github | lower }}.srvzct-52.he-arc.ch;

    location / {
        proxy_pass http://localhost:{{ user.http }}/;
    }
}

{%- endfor %}
""")

template = Template("""\
version: "2"

services:
{%- for user in users %}
  {{ user.machine }}:
    image: greut/webapp-server:rails
    environment:
      GROUPNAME: "{{ user.groupname }}"
      PASSWORD: "{{ user.password }}"
      LONE_WOLF: "true"
    hostname: {{ user.hostname }}
    domainname: srvz-webapp.he-arc.ch
    volumes:
      - {{ user.machine }}:/var/www
      - ./config:/root/config:ro
    ports:
      - "{{ user.ssh }}:22"
      - "{{ user.http }}:80"
      - "{{ user.jupyter }}:8888" # iruby (jupyter)
    depends_on:
      - postgres
      - mysql
      - smtp

    #links:
    #  - {{ user.machine }}_redis:redis

  #{{ user.machine }}_redis:
  #  image: redis:3.2-alpine
{% endfor %}

  # Remember to change both passwords after the boot!
  mysql:
    image: mysql:5.7
    environment:
      - MYSQL_ROOT_PASSWORD=root
    ports:
      - "3306:3306"
    volumes:
      - mysql:/var/lib/mysql

  postgres:
    image: mdillon/postgis:9.6
    environment:
      - POSTGRES_PASSWORD=root
      - POSTGRES_PGDATA=/var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
     - postgres:/var/lib/postgresql/data

  smtp:
    image: mailhog/mailhog:latest
    ports:
      - "8025:8025"

volumes:
  postgres:
  mysql:
  # users
{% for user in users %}
  {{ user.machine }}:
{%- endfor -%}
""")


def main(argv):
    students = argv[1]
    destination = argv[2]
    nginx_conf = argv[3]

    users = []
    counter = 0

    with open(students, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        # skip headers
        next(reader)
        for student in map(StudentRecord._make, reader):
            if len(student.email) < 5:
                continue

            groupname = student.email.replace('.', '_')
            users.append(
                User(
                    machine=groupname,
                    groupname=groupname,
                    hostname=student.email,
                    password=passgen(punctuation=False),
                    github=student.github,
                    ssh=2200 + counter,
                    http=8000 + counter,
                    jupyter=8800 + counter))
            counter += 1

    with open(destination, 'w', encoding='utf-8') as f:
        f.write(template.render(users=users))
    with open(nginx_conf, 'w', encoding='utf-8') as f:
        f.write(nginx.render(users=users))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
