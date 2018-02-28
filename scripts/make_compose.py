#!/usr/bin/env python3
"""
Team2 Compose
-------------

Create the docker-compose YAML file for a team.
"""

import argparse
import csv
import sys

from collections import namedtuple
from jinja2 import Template
from passgen import passgen

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.4.0"

domainname = "srvz-webapp.he-arc.ch"
admin = "teacher"

Team = namedtuple("Team", "machine image hostname groupname password ssh_keys")
StudentRecord = namedtuple("StudentRecord",
                           "lastname, firstname, email, classname, github, "
                           "image1, team1, image2, team2, comment, week")

template = Template("""\
version: "3.2"

services:
{%- for team in teams %}
  {{ team.machine }}:
    image: hearcch/webapp-server:{{ team.image }}
    hostname: {{ team.hostname }}
    environment:
      GROUPNAME: {{ team.groupname }}
      PASSWORD: {{ team.password }}
      SSH_KEYS: {{ team.ssh_keys | join(" ") }}
    volumes:
      - {{ team.machine }}:/var/www

    ports:
      - "2200:22"  # to be manually configured.

    external_links:
      - postgres
      - mysql
      - smtp

    links:
      - {{ team.machine }}_redis:redis

    labels:
      - "traefik.frontend.rule=Host:{{ team.hostname }}.{{ domainname }}"
      - "traefik.port=80"

  {{ team.machine }}_redis:
    image: redis:3.2-alpine
    volumes:
      - {{ team.machine }}_redis:/data
    labels:
      - "traefik.enable=false"
{%- endfor %}

networks:
  default:
    external:
      name: webapp-net

volumes:
  postgres:
  mysql:
  # teams
{% for team in teams %}
  {{ team.machine }}:
  {{ team.machine }}_redis:
{%- endfor -%}
""")


def main():
    parser = argparse.ArgumentParser(description="docker-compose.yml builder")
    parser.add_argument("team", type=str, help="team name")

    args = parser.parse_args()

    teams = {}

    reader = csv.reader(sys.stdin, delimiter="\t")
    # skip headers
    next(reader)
    for student in map(StudentRecord._make, reader):
        # groupname
        groupname = None
        if (args.team in (student.team1, student.team2)
                or student.classname == admin):
            groupname = args.team.lower()

        # imagename
        image = None
        if args.team == student.team1:
            image = student.image1
        elif args.team == student.team2:
            image = student.image2

        if groupname:
            # XXX admin group must be after the others
            if groupname not in teams:
                teams[groupname] = Team(
                    image=image.lower(),
                    machine=groupname,
                    groupname=groupname,
                    hostname=groupname,
                    password=passgen(punctuation=False),
                    ssh_keys={student.github})
            else:
                teams[groupname].ssh_keys.add(student.github)

    print(template.render(teams=teams.values(), domainname=domainname))


if __name__ == "__main__":
    sys.exit(main())
