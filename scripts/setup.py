#!/usr/bin/env python3
"""
Setup
-----

Create the environment, users with all the required files.
"""

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.7.0"

import os
import csv
import sys
import pwd
import random

from collections import namedtuple
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("/var/templates"))
wwwdir = "/var/www"

ADMIN = "teachers"
STUDENTS = "/root/config/students.tsv"

StudentRecord = namedtuple(
    "StudentRecord", "lastname, firstname, email, classname, github, "
    "image1, team1, image2, team2, comment, week"
)


def authorized_keys(username, github):
    """Copy the user key into the authorized keys."""
    p = pwd.getpwnam(username)
    homedir, uid, gid = p.pw_dir, p.pw_uid, p.pw_gid

    authorized_keys = os.path.join(homedir, ".ssh/authorized_keys")
    key = "/root/config/keys/{}.key".format(github)
    if os.path.exists(key):
        with open(key, "r") as f:
            with open(authorized_keys, "a+") as t:
                t.write(f.read())
        os.chown(authorized_keys, uid, gid)
        os.chmod(authorized_keys, mode=0o0600)
    else:
        sys.stderr.write("No public key for {}!\n".format(github))


def main(argv):
    # Load global conf
    environ = os.environ

    groupname = environ["GROUPNAME"]
    config = environ["CONFIG"]
    poweruser = environ.get("POWERUSER", "poweruser")

    # Global environment "variables"
    environ["MYSQL_HOST"] = environ.get("MYSQL_HOST", "mysql")
    environ["MYSQL_PORT"] = environ.get("MYSQL_PORT", "3306")
    environ["POSTGRES_HOST"] = environ.get("POSTGRES_HOST", "postgres")
    environ["POSTGRES_PORT"] = environ.get("POSTGRES_PORT", "5432")
    environ["REDIS_HOST"] = environ.get("REDIS_HOST", "redis")
    environ["REDIS_PORT"] = environ.get("REDIS_PORT", "6379")
    environ["SMTP_HOST"] = environ.get("SMTP_HOST", "smtp")
    environ["SMTP_PORT"] = environ.get("SMTP_PORT", "1025")

    if config == "Rails":
        environ["SECRET_KEY_BASE"] = "{:0128x}".format(
            random.randrange(16**128))
    elif config == "Python":
        environ["SECRET_KEY"] = "{:0128x}".format(random.randrange(16**128))

    os.mkdir("/etc/container_environment")
    for k, v in environ.items():
        if k == "HOME":
            continue
        with open("/etc/container_environment/{0}".format(k), "w+") as f:
            f.write(v)

    # Create users
    if (os.path.exists(STUDENTS)):
        with open(STUDENTS, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            # skip headers
            next(reader)
            for student in map(StudentRecord._make, reader):
                groups = {
                    t.strip().lower()
                    for t in (student.team1, student.team2)
                }

                # Only pick the users of the given group (or admin)
                if not groups.isdisjoint((groupname.lower(), ADMIN)):
                    authorized_keys(poweruser, student.github)
                    sys.stderr.write("{} is {}.\n".format(poweruser, student.github))
    else:
        sys.stderr.write("No {} file found.\n".format(STUDENTS))

    sys.stderr.write("Setup is done.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
