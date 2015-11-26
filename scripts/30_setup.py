#!/usr/bin/env python3
"""
Setup
-----

Create the environment, users with all the required files.
"""

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.2"

import re
import os
import csv
import sys
import pwd
import json
import shutil
import os.path
import subprocess
import unicodedata
import multiprocessing

from collections import namedtuple
from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader("/var/templates"))
wwwdir = "/var/www"


def formatUserName(firstname):
    """
    Format the real name into a username

    E.g.: Juan Giovanni Di Sousa Santos -> juan
    """
    # Keep only the first firstname
    first = re.match("^(.+?)\\b", firstname, re.U).group(0).lower()

    username = unicodedata.normalize("NFD", first)
    username = username.replace(" ", "")
    # http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string/517974#517974
    return "".join([c for c in username if not unicodedata.combining(c)])


def init_user(username, groupname, **kwargs):
    """As the user."""
    p = pwd.getpwnam(username)
    uid, gid = p.pw_uid, p.pw_gid
    homedir = p.pw_dir

    os.initgroups(groupname, gid)
    os.setgid(gid)
    os.setuid(uid)
    os.chdir(homedir)
    os.umask(0o002)  # readable by group members

    os.environ["USER"] = username
    os.environ["HOME"] = homedir
    os.environ["UID"] = str(uid)

    paths = [("bash_profile", ".bash_profile"),
             ("gitconfig", ".gitconfig"),
             ("vimrc", ".vimrc")]
    config = kwargs["environ"].get("CONFIG", None)
    if config == "Laravel":
        paths.append(("README-php.md", "README.md"))
    if config == "Rails":
        paths.append(("README-ror.md", "README.md"))
    for tpl, dest in paths:
        if not os.path.exists(dest):
            render(tpl, dest, username=username, groupname=groupname, **kwargs)

    # link /var/www to ~/www
    os.symlink(wwwdir, "www")

    # Create .ssh/authorized_keys
    os.mkdir(".ssh")
    os.chmod(".ssh", mode=0o0700)

    # Vim
    os.mkdir(".vim")
    os.mkdir(".vim/bundle")

    # Vundle
    shutil.copytree("/var/Vundle.vim", ".vim/bundle/Vundle.vim")
    subprocess.check_call(["vim", "+PluginInstall", "+qall!"],
                          stderr=subprocess.PIPE,
                          stdout=subprocess.PIPE)

    # Laravel installer
    if kwargs["environ"]["CONFIG"] == "Laravel":
        sys.stderr.write("Running composer global require laravel/installer\n")
        """ works, so ignore it.
        subprocess.check_call(["composer",
                               "global",
                               "require",
                               "laravel/installer=~1.1"],
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        """


def create_user(username, groupname, comment, environ=None):
    """
    Create a UNIX user (the group must exist beforehand)
    """
    groups = ["users"]
    if environ is not None and environ.get("CONFIG", None) == "Rails":
        groups.append("rvm")

    subprocess.check_call(["useradd", username,
                           "-c", comment,
                           "--create-home",
                           "--no-user-group",
                           "--shell", "/bin/bash",
                           "--groups", ",".join(groups)],
                          stderr=subprocess.PIPE,
                          stdout=subprocess.PIPE)
    subprocess.check_call(["usermod", username,
                           "--gid", groupname,
                           "--groups", "{},users".format(groupname)],
                          stderr=subprocess.PIPE,
                          stdout=subprocess.PIPE)
    proc = subprocess.Popen(["chpasswd"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc.communicate("{}:{}".format(username, pwgen()).encode("utf-8"))


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
    """As the user representing the group."""
    p = pwd.getpwnam(groupname)
    uid, gid = p.pw_uid, p.pw_gid
    homedir = p.pw_dir

    os.initgroups(groupname, gid)
    os.setgid(gid)
    os.setuid(uid)
    os.chdir(homedir)
    os.umask(0o002)  # readable by group members

    config = kwargs["environ"].get("CONFIG", None)

    paths = []
    dirs = ["config", "logs"]

    if config == "Laravel":
        dirs.append("public")

        paths = (("index.php", "public/index.php"),
                 ("nginx-php.conf", "config/nginx.conf"))

    if config == "Rails":
        dirs.append("app/public")
        dirs.append(".gem/ruby/2.2.0")

        paths = (("nginx-ror.conf", "config/nginx.conf"),
                 ("uwsgi.ini", "config/uwsgi.ini"),
                 ("Gemfile", "app/Gemfile"),
                 ("Gemfile.lock", "app/Gemfile.lock"),
                 ("config.ru", "app/config.ru"))

    for p in dirs:
        if not os.path.exists(p):
            os.makedirs(p)

    for tpl, dest in paths:
        if not os.path.exists(dest):
            render(tpl, dest, groupname=groupname, **kwargs)

    if config == "Rails":
        shutil.copy2("/var/templates/uwsgi-nginx.jpg", "app/public")

    return homedir, uid, gid


def create_group(groupname):
    """Create the system user named after the group."""
    subprocess.check_call(["useradd", groupname,
                           "-c", "GROUP",
                           "--no-create-home",
                           "--home-dir", wwwdir,
                           "--user-group",
                           "--system"],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)
    subprocess.check_call(["usermod", "--lock", groupname],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)


def render(template, path, **kwargs):
    if not os.path.exists(path):
        template = env.get_template(template)
        with open(path, "w", encoding="utf-8") as f:
            f.write(template.render(**kwargs))


def pwgen(length=128):
    """Generates a secure password."""
    proc = subprocess.Popen(["pwgen", "--secure", "{}".format(length), "1"],
                            stdout=subprocess.PIPE)
    return proc.communicate()[0].decode().strip()


def main(argv):
    # Load global conf
    conf = "/etc/container_environment.json"
    with open(conf, "r", encoding="utf-8") as f:
        environ = json.load(f)

    groupname = environ["GROUPNAME"]
    if "MYSQL_PORT_3306_TCP_ADDR" in environ:
        environ["MYSQL_HOST"] = environ["MYSQL_PORT_3306_TCP_ADDR"]
        environ["MYSQL_PORT"] = environ["MYSQL_PORT_3306_TCP_PORT"]
        del environ["MYSQL_PORT_3306_TCP_ADDR"]
        del environ["MYSQL_PORT_3306_TCP_PORT"]
        if "MYSQL_ENV_MYSQL_ROOT_PASSWORD" in environ:
            del environ["MYSQL_ENV_MYSQL_ROOT_PASSWORD"]

    if "POSTGRES_PORT_5432_TCP_ADDR" in environ:
        environ["POSTGRES_HOST"] = environ["POSTGRES_PORT_5432_TCP_ADDR"]
        environ["POSTGRES_PORT"] = environ["POSTGRES_PORT_5432_TCP_PORT"]
        del environ["POSTGRES_PORT_5432_TCP_ADDR"]
        del environ["POSTGRES_PORT_5432_TCP_PORT"]
        if "POSTGRES_ENV_POSTGRES_PASSWORD" in environ:
            del environ["POSTGRES_ENV_POSTGRES_PASSWORD"]

    if "REDIS_PORT_6379_TCP_ADDR" in environ:
        environ["REDIS_HOST"] = environ["REDIS_PORT_6379_TCP_ADDR"]
        environ["REDIS_PORT"] = environ["REDIS_PORT_6379_TCP_PORT"]

    if "MEMCACHED_PORT_11211_TCP_ADDR" in environ:
        environ["MEMCACHED_HOST"] = environ["MEMCACHED_PORT_11211_TCP_ADDR"]
        environ["MEMCACHED_PORT"] = environ["MEMCACHED_PORT_11211_TCP_PORT"]

    del environ["LC_CTYPE"]
    del environ["LANG"]
    del environ["INITRD"]

    # Create the group
    try:
        p = pwd.getpwnam(groupname)
        sys.stderr.write("Setup already done!\n")
        return 0
    except KeyError:
        pass

    # Configure SSMTP
    subprocess.check_call(["sed",
                           "-i",
                           "s/mailhub=mail/mailhub={}:{}/".format(
                               environ["MAILCATCHER_PORT_1025_TCP_ADDR"],
                               environ["MAILCATCHER_PORT_1025_TCP_PORT"]),
                           "/etc/ssmtp/ssmtp.conf"],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)


    # Create the group
    create_group(groupname)
    p = pwd.getpwnam(groupname)
    uid, gid = p.pw_uid, p.pw_gid
    # Rights for existing files
    os.chown(wwwdir, uid, gid)
    os.chmod(wwwdir, mode=0o0775)
    for root, dirs, files in os.walk(wwwdir):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o0775)
            os.chown(os.path.join(root, d), uid, gid)
        for f in files:
            os.chmod(os.path.join(root, f), 0o0664)
            os.chown(os.path.join(root, f), uid, gid)


    # Init the group files
    p = multiprocessing.Process(target=init_group,
                                args=(groupname,),
                                kwargs=dict(environ=environ))
    p.start()
    p.join()

    # symlink the server config
    os.symlink("/var/www/config/nginx.conf",
               "/etc/nginx/sites-enabled/{}".format(groupname))

    # Create users
    students = "/root/config/students.tsv"
    StudentRecord = namedtuple("StudentRecord",
                               "lastname, firstname, email, classname, room, "
                               "group, github, comment")
    if (os.path.exists(students)):
        with open(students, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            # skip headers
            next(reader)
            for student in map(StudentRecord._make, reader):
                # Only pick the users of the given group
                if student.group in (groupname, "admin"):
                    username = formatUserName(student.firstname)
                    create_user(username, groupname, student.classname, environ)
                    p = multiprocessing.Process(target=init_user,
                                                args=(username,
                                                      groupname),
                                                kwargs=dict(environ=environ,
                                                            **student._asdict()))
                    p.start()
                    p.join()
                    authorized_keys(username, student.github)
                    sys.stderr.write("{} created.\n".format(username))
    else:
        sys.stderr.write("No {} file found.\n".format())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
