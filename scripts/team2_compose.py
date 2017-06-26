#!/usr/bin/env python3
"""
Team2 Compose
-------------

Create the docker-compose YAML file for the second team
"""

import csv
import sys

from collections import namedtuple
from jinja2 import Template
from passgen import passgen

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.1.0"

domainname = "srvz-webapp.he-arc.ch"

Team = namedtuple("Team", "machine image hostname groupname password ssh http")
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
<h2>Équipes</h2>
<ol>
{%- for team in teams %}
    <li value="{{ team.ssh }}"><a href="http://{{ team.hostname }}.{{ domainname }}">{{ team.hostname }}</a>
{%- endfor %}
</ol>
""")

nginx = Template("""\
map $http_upgrade $connection_upgrade {
    default Upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;

    server_name webmail.{{ domainname }};

    location / {
        proxy_pass http://localhost:8125;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;

        # WebSocket support.
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $http_connection;
    }
}

{%- for team in teams %}
server {
    listen 80;
    listen [::]:80;

    server_name {{ team.hostname }}.{{ domainname }};

    location / {
        proxy_pass http://localhost:{{ team.http }}/;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $http_connection;
        proxy_pass http://localhost:{{ team.http }}/ws;
    }
}

{%- endfor %}
""")

template = Template("""\
version: "2"

services:
{%- for team in teams %}
  {{ team.machine }}:
    image: hearcch/webapp-server:{{ team.image }}
    environment:
      GROUPNAME: "{{ team.groupname }}"
      PASSWORD: "{{ team.password }}"
    hostname: {{ team.hostname }}
    domainname: {{ domainname }}
    volumes:
      - {{ team.machine }}:/var/www
      - ./config:/root/config:ro
    ports:
      - "{{ team.ssh }}:22"
      - "{{ team.http }}:80"
    depends_on:
      - postgres
      - mysql
      - smtp

    links:
      - {{ team.machine }}_redis:redis

  {{ team.machine }}_redis:
    image: redis:3.2-alpine
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
    image: mdillon/postgis:9.6-alpine
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
  # teams
{% for team in teams %}
  {{ team.machine }}:
{%- endfor -%}
""")


def main(argv):
    students = argv[1]
    destination = argv[2]
    nginx_conf = argv[3]
    index_html = argv[4]

    teams = {}

    with open(students, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        # skip headers
        next(reader)
        for student in map(StudentRecord._make, reader):
            groupname = student.team2
            if groupname and groupname not in teams and student.image2:
                teams[groupname] = Team(
                    image=student.image2.lower(),
                    machine=groupname.lower(),
                    groupname=groupname,
                    hostname=groupname.lower(),
                    password=passgen(punctuation=False),
                    ssh=2200 + len(teams),
                    http=8000 + len(teams))

    with open(destination, 'w', encoding='utf-8') as f:
        f.write(template.render(teams=teams.values(), domainname=domainname))
    with open(nginx_conf, 'w', encoding='utf-8') as f:
        f.write(nginx.render(teams=teams.values(), domainname=domainname))
    with open(index_html, 'w', encoding='utf-8') as f:
        f.write(index.render(teams=teams.values(), domainname=domainname))


if __name__ == "__main__":
    print("THIS FORMAT IS OUTDATED!")
    #sys.exit(main(sys.argv))
