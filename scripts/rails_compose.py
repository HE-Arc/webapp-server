#!/usr/bin/env python3
"""
Rails Compose
-------------

Create the docker-compose YAML file for the users.
"""

import csv
import sys

from collections import namedtuple
from jinja2 import Template
from passgen import passgen

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.1.0"

domainname = "srvz-webapp2.he-arc.ch"

User = namedtuple("User",
                  "machine hostname github groupname password ssh http")
StudentRecord = namedtuple("StudentRecord",
                           "lastname, firstname, email, classname, github, "
                           "image1, team1, image2, team2, comment, week")

index = Template("""\
<!DOCTYPE html>
<meta charset=utf-8>
<title>{{ domainname }}</title>

<h1>Domains</h1>
<p>
    <a href="http://webmail.{{ domainname }}">Webmail</a>
</p>
<h2>Users</h2>
<ol start=2200>
{%- for user in users %}
    <li><a href="http://{{ user.hostname }}.{{ domainname }}">{{ user.hostname }}</a>
        (<a href="http://{{ user.github | lower }}.{{ domainname }}">@{{ user.github }}</a>)
{%- endfor %}
</ol>
""")

nginx = Template("""\
server {
    listen 80;
    listen [::]:80;

    server_name webmail.{{ domainname }};

    location / {
                 proxy_pass http://localhost:8125;
    }
}

{%- for user in users %}
server {
    listen 80;
    listen [::]:80;

    server_name {{ user.hostname }}.{{ domainname }} {{ user.github | lower }}.{{ domainname }};

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
    image: hearcch/webapp-server:rails
    environment:
      GROUPNAME: "{{ user.groupname }}"
      PASSWORD: "{{ user.password }}"
      LONE_WOLF: "true"
    hostname: {{ user.hostname }}
    domainname: {{ domainname }}
    volumes:
      - {{ user.machine }}:/var/www
      - ./config:/root/config:ro
    ports:
      - "{{ user.ssh }}:22"
      - "{{ user.http }}:80"
    depends_on:
      - postgres
      #- mysql
      - smtp

    #links:
    #  - {{ user.machine }}_redis:redis

  #{{ user.machine }}_redis:
  #  image: redis:3.2-alpine
{% endfor %}

  # Remember to change both passwords after the boot!
  #mysql:
  #  image: mysql:5.7
  #  environment:
  #    - MYSQL_ROOT_PASSWORD=root
  #  ports:
  #    - "3306:3306"
  #  volumes:
  #    - mysql:/var/lib/mysql

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
      - "8125:8025"

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
    index_html = argv[4]

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
                    http=8000 + counter))
            counter += 1

    with open(destination, 'w', encoding='utf-8') as f:
        f.write(template.render(users=users, domainname=domainname))
    with open(nginx_conf, 'w', encoding='utf-8') as f:
        f.write(nginx.render(users=users, domainname=domainname))
    with open(index_html, 'w', encoding='utf-8') as f:
        f.write(index.render(users=users, domainname=domainname))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
