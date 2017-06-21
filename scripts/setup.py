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
    poweruser = environ.get("POWERUSER", "poweruser")

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
