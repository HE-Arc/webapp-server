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
import shutil
import subprocess
import multiprocessing

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



def check_call(command, env, stderr=sys.stderr, stdout=sys.stderr):
    subprocess.check_call(command, env=env, stderr=stderr, stdout=stdout)


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


def init_group(groupname, **kwargs):
    """Init the group as the user representing it."""
    p = pwd.getpwnam(groupname)
    uid, gid = p.pw_uid, p.pw_gid
    homedir = p.pw_dir

    os.initgroups(groupname, gid)
    os.setgid(gid)
    os.setuid(uid)
    os.chdir(wwwdir)

    # Randomize the password, for good measure.
    proc = subprocess.Popen(
        ["chpasswd"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    password = "{:064x}".format(random.randrange(16**64))
    proc.communicate("{}:{}".format(groupname, password).encode('utf-8'))

    config = kwargs["environ"].get("CONFIG", None)
    environ = kwargs["environ"].copy()
    environ["HOME"] = homedir

    paths = []
    dirs = ["config", "logs"]

    if config == "Laravel":
        dirs.append("public")

        paths = (("laravel/app/index.php", "public/index.php"),
                 ("laravel/config/php-fpm.conf", "config/php-fpm.conf"),
                 ("laravel/config/nginx.conf", "config/nginx.conf"))

    elif config == "Rails":
        dirs.append("app/public")
        dirs.append(kwargs["environ"]["GEM_HOME"])

        paths = (("rails/config/nginx.conf", "config/nginx.conf"),
                 ("rails/config/puma.rb", "config/puma.rb"),
                 ("rails/app/Gemfile", "app/Gemfile"),
                 ("rails/app/config.ru", "app/config.ru"))

    for p in dirs:
        if not os.path.exists(p):
            os.makedirs(p)

    for tpl, dest in paths:
        if not os.path.exists(dest):
            render(tpl, dest, groupname=groupname, **kwargs)

    if config == "Rails":
        shutil.copy2("/var/templates/rails/app/public/nginx-puma.png",
                     "app/public")

        sys.stderr.write("Running Bundler installation.\n")
        check_call(
            ["gem", "install", "bundler", "puma"], env=kwargs["environ"])
        os.chdir('app')
        check_call(
            ["{0}/bin/bundler".format(environ["GEM_HOME"]), "install"],
            env=kwargs["environ"])
        os.chdir(homedir)

    return homedir, uid, gid


def render(template, path, **kwargs):
    """Render a Jinja2 template into the given file."""
    if not os.path.exists(path):
        template = env.get_template(template)
        with open(path, "w", encoding="utf-8") as f:
            f.write(template.render(**kwargs))


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

    if config == "Laravel":
        environ["COMPOSER_HOME"] = "/var/www/.composer"
    elif config == "Rails":
        environ["GEM_HOME"] = "/var/www/.gem/ruby/2.4.0"
        environ["SECRET_KEY_BASE"] = "{:0128x}".format(
            random.randrange(16**128))
    elif config == "Python":
        environ["SECRET_KEY"] = "{:0128x}".format(random.randrange(16**128))

    if os.path.exists('/etc/container_environment'):
        sys.stderr.write("Setup was done earlier.\n")
        return 0

    os.mkdir("/etc/container_environment")
    for k, v in environ.items():
        if k == "HOME":
            continue
        with open("/etc/container_environment/{0}".format(k), "w+") as f:
            f.write(v)

    # Init the group files
    p = multiprocessing.Process(
        target=init_group, args=(poweruser, ), kwargs=dict(environ=environ))
    p.start()
    p.join()

    assert p.exitcode == 0, "init_group failed."

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
