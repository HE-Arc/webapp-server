#!/usr/bin/env python3
"""
Nginx
-----

Sets up the system.

- nginx configuration file.
- index.php

"""

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.1a2"

import re
import os
import csv
import sys
import pwd
import json
import shutil
import pymysql
import os.path
import requests
import platform
import subprocess
import unicodedata

from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader("/root/templates"))
wwwdir = "/var/www"


def formatUserName(firstname, lastname):
    """
    Format the real name into a username

    E.g.: Juan Giovanni Di Sousa Santos -> juan.disousa
    """
    # Keep only the first firstname
    first = re.match("^(.+?)\\b", firstname, re.U).group(0).lower()
    # Keep only the first two lastnames
    last = re.match("^(.+?(?:$|\\s.+?\\b))", lastname, re.U).group(0).lower()

    username = unicodedata.normalize("NFD", "{}.{}".format(first,last))
    username = username.replace(" ", "")
    # http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string/517974#517974
    return "".join([c for c in username if not unicodedata.combining(c)])


def laravel(homedir, username, uid, gid):
    """Install Laravel and Composer from local cache."""

    shutil.copy("/root/composer.phar", os.path.join(homedir, "composer.phar"))
    os.chown(os.path.join(homedir, "composer.phar"), uid, gid)
    os.chmod(os.path.join(homedir, "composer.phar"), 0o644)

    shutil.copytree("/root/.composer", os.path.join(homedir, ".composer"))
    os.chown(os.path.join(homedir, ".composer"), uid, gid)
    os.chmod(os.path.join(homedir, ".composer"), 0o755)
    for root, dirs, files in os.walk(os.path.join(homedir, ".composer")):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
            os.chown(os.path.join(root, d), uid, gid)
        for f in files:
            os.chmod(os.path.join(root, f), 0o644)
            os.chown(os.path.join(root, f), uid, gid)

    # Le symlink
    os.symlink(os.path.join(homedir, ".composer", "vendor", "laravel", "installer", "laravel"),
               os.path.join(homedir, ".composer", "vendor", "bin", "laravel"))
    os.chmod(os.path.join(homedir, ".composer", "vendor", "laravel", "installer", "laravel"), 0o0755)


def user(mysql_password, lastname, firstname, classname, groupname, github, comment):
    """
    Create a user.
    """
    username = formatUserName(firstname, lastname)
    homedir = os.path.join("/home", username)
    fullname = "{} {}".format(firstname, lastname)

    cmd = ["useradd", username,
    #       "-c", fullname,
            "-c", github,
            "--create-home",
            "--home-dir", homedir,
            "--no-user-group",
            "--shell", "/bin/bash",
            "--groups", "users"]
    subprocess.check_call(cmd)
    proc = subprocess.Popen(["chpasswd"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc.communicate("{}:{}".format(username, pwgen()).encode("utf-8"))

    p = pwd.getpwnam(username)
    uid, gid = p.pw_uid, p.pw_gid

    # link /var/www to /home/me/www
    os.symlink(wwwdir, os.path.join(homedir, "www"))
    os.chown(os.path.join(homedir, "www"), uid, gid)
    os.chmod(os.path.join(homedir, "www"), 0o755)

    # .ssh
    sshdir = os.path.join(homedir, ".ssh")
    os.mkdir(sshdir)
    os.chown(sshdir, uid, gid)
    os.chmod(sshdir, 0o700)

    # Create authorized_keys
    r = requests.get("https://api.github.com/users/{}/keys".format(github),
                     auth=(os.environ["GITHUB_USER"], os.environ["GITHUB_KEY"]))
    if r.ok:
        #sys.stderr.write("{}:{} is {}\n".format(username, groupname, github))
        keys = r.json()
        authorized_keys = os.path.join(sshdir, "authorized_keys")
        with open(authorized_keys, "a+") as fa:
            for key in keys:
                fa.write(key["key"])
                fa.write(" ")
                fa.write(username)
                fa.write(" is ")
                fa.write(github)
                fa.write("\n")

        os.chown(authorized_keys, uid, gid)
        os.chmod(authorized_keys, 0o600)

    else:
        sys.stderr.write(r.text)
        sys.stderr.write("\nCannot grab github key of {}\n".format(github))

    fullname = "{} {}".format(firstname, lastname)

    # Load global conf
    conf = "/etc/container_environment.json"
    with open(conf, "r", encoding="utf-8") as f:
        envs = json.load(f)

    del envs["MYSQL_ENV_MYSQL_ROOT_PASSWORD"]
    envs["MYSQL_HOST"] = "mysql"  # cheat
    envs["MYSQL_PORT"] = os.environ["MYSQL_PORT_3306_TCP_PORT"]
    envs["MYSQL_DATABASE"] = groupname
    envs["MYSQL_USERNAME"] = groupname
    envs["MYSQL_PASSWORD"] = mysql_password

    # Create .bash_profile
    template = env.get_template("bash_profile")
    bashrc = os.path.join(homedir, ".bash_profile")
    with open(bashrc, "w+", encoding="utf-8") as f:
        f.write(template.render(fullname=fullname, groupname=groupname,
                                classname=classname, envs=envs))
    os.chown(bashrc, uid, gid)

    # Create README.txt
    template = env.get_template("README.txt")
    readme = os.path.join(homedir, "README.txt")
    with open(readme, "w+", encoding="utf-8") as f:
        f.write(template.render(fullname=fullname, groupname=groupname,
                                username=username, classname=classname))
    os.chown(readme, uid, gid)

    # Install Laravel
    laravel(homedir, username, uid, gid)

    return username, uid, gid


def users(groupname, filename, mysql_password):
    """
    Read the tsv file and create the users.
    """

    with open(filename, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        # skip headers
        next(reader)
        for row in reader:
            # Only pick the users of the given group
            if row[3] in (groupname, "admin"):
                # admin become part of the group
                row[3] = groupname
                username, uid, gid = user(mysql_password, *row)
                sys.stderr.write("{} ({}:{}) created.\n".format(username, uid, gid))

    return 0


def nginx(**kwargs):
    """Create the nginx sites-available configuration file."""
    template = env.get_template("nginx")

    group = kwargs["groupname"]

    available = "/etc/nginx/sites-available/{}".format(group)
    enabled = "/etc/nginx/sites-enabled/{}".format(group)

    if not os.path.exists(available):
        with open(available, "w", encoding="utf-8") as f:
            f.write(template.render(**kwargs))

        if not os.path.exists(enabled):
            os.symlink(available, enabled)


def phpinfo(group):
    """
    Create a sample phpinfo()
    """
    template = env.get_template("index.php")

    info = "/var/www/index.php".format(group)

    if not os.path.exists(info):
        with open(info, "w", encoding="utf-8") as f:
            f.write(template.render(group=group))

        p = pwd.getpwnam(group)

        os.chown(info, p.pw_uid, p.pw_gid)
        os.chmod(info, 0o0664)


def rights():
    """
    Fixes the rights on the mounted volume.
    """
    p = pwd.getpwnam("yoan.blanc")  # FIXME ugly!

    os.chown(wwwdir, p.pw_uid, p.pw_gid)
    os.chmod(wwwdir, 0o775)


def pwgen():
    """Generates a *solid* password."""
    proc = subprocess.Popen(["pwgen"], stdout=subprocess.PIPE)
    return proc.communicate()[0].decode().strip()


def database(groupname, host, port, password):
    """
    Creates the database for the group.
    """

    password_file = os.path.join(wwwdir, ".mysql_password")

    conn = pymysql.connect(host=host,
                           user="root",
                           password=password,
                           charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor)

    try:
        create_db = False
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s;", (groupname,))
            if cursor.fetchone() is None:
                create_db = True
        conn.rollback()

        if create_db:
            password = pwgen()

            with conn.cursor() as cursor:
                cursor.execute("CREATE USER %s@%s;", (groupname, '%'))
                cursor.execute("SET PASSWORD FOR %s@%s = PASSWORD(%s);",
                               (groupname, '%', password))
                cursor.execute("CREATE DATABASE `{}`"
                               " DEFAULT CHARACTER SET utf8mb4"
                               " DEFAULT COLLATE utf8mb4_unicode_ci;".format(groupname))
                cursor.execute("GRANT ALL PRIVILEGES ON {}.* TO %s@%s;".format(groupname),
                               (groupname, '%'))
            conn.commit()

            with open(password_file, "w+") as f:
                f.write(password)
                sys.stderr.write("{}: {}\n".format(password_file, password))
        else:
            with open(password_file, "r", encoding="utf-8") as f:
                password = f.read().strip()
    finally:
        conn.close()

    # test the connection!
    conn = pymysql.connect(host=host,
                           user=groupname,
                           password=password,
                           db=groupname,
                           charset="utf8mb4",
                           cursorclass=pymysql.cursors.DictCursor)

    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            sys.stderr.write("Tables of {}\n".format(groupname))
            for row in cursor.fetchall():
                sys.stderr.write(" {}\n".format(row))
    finally:
        conn.close()

    return password


def main(argv):
    # ENV
    groupname = os.environ["GROUPNAME"]
    mysql_host = os.environ["MYSQL_PORT_3306_TCP_ADDR"]
    mysql_port = os.environ["MYSQL_PORT_3306_TCP_PORT"]
    hostname = platform.node()
    os.environ["HOSTNAME"] = hostname

    # Create MYSQL database ;-)
    root = os.environ["MYSQL_ENV_MYSQL_ROOT_PASSWORD"]
    mysql_password = database(groupname, mysql_host, mysql_port, root)
    del os.environ["MYSQL_ENV_MYSQL_ROOT_PASSWORD"]  # clean up

    # Update env!
    os.environ["MYSQL_USERNAME"] = groupname
    os.environ["MYSQL_DATABASE"] = groupname
    os.environ["MYSQL_PASSWORD"] = mysql_password

    # Create users
    students = "/root/students.tsv"
    if (os.path.exists(students)):
        users(groupname, students, mysql_password)
        os.unlink(students)

    # Create nginx config
    nginx(groupname=groupname, hostname=hostname, mysql_password=mysql_password)
    # fix the rights on www
    rights()
    # setup the phpinfo file.
    phpinfo(groupname)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
