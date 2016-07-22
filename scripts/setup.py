#!/usr/bin/env python3
"""
Setup
-----

Create the environment, users with all the required files.
"""

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.3"

import re
import os
import csv
import sys
import pwd
import random
import shutil
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

    os.environ["USER"] = username
    os.environ["HOME"] = homedir
    os.environ["UID"] = str(uid)

    paths = [("bash_profile", ".bash_profile"),
             ("gitconfig", ".gitconfig")]
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

    # Laravel installer
    if kwargs["environ"]["CONFIG"] == "Laravel":
        sys.stderr.write("Running composer global require laravel/installer\n")
        subprocess.check_call(["composer",
                               "global",
                               "require",
                               "laravel/installer=~1.3"],
                              stderr=sys.stderr,
                              stdout=sys.stdout)


def create_user(username, groupname, comment):
    """Create a UNIX user (the group must exist beforehand)."""
    groups = ["users"]

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
    """Init the group as the user representing it."""
    p = pwd.getpwnam(groupname)
    uid, gid = p.pw_uid, p.pw_gid
    homedir = p.pw_dir

    os.initgroups(groupname, gid)
    os.setgid(gid)
    os.setuid(uid)
    os.chdir(homedir)

    config = kwargs["environ"].get("CONFIG", None)

    paths = []
    dirs = ["config", "logs"]

    if config == "Laravel":
        dirs.append("public")

        paths = (("index.php", "public/index.php"),
                 ("nginx-php.conf", "config/nginx.conf"))

    elif config == "Rails":
        dirs.append("app/public")
        dirs.append(kwargs["environ"]["GEM_HOME"])

        paths = (("nginx-ror.conf", "config/nginx.conf"),
                 ("puma.rb", "config/puma.rb"),
                 ("Gemfile", "app/Gemfile"),
                 ("Gemfile.lock", "app/Gemfile.lock"),
                 ("config.ru", "app/config.ru"))

    else:
        dirs.append("public")

        paths = (("nginx-base.conf", "config/nginx.conf"),
                 ("hello.html", "public/index.html"))

    for p in dirs:
        if not os.path.exists(p):
            os.makedirs(p)

    for tpl, dest in paths:
        if not os.path.exists(dest):
            render(tpl, dest, groupname=groupname, **kwargs)

    if config == "Rails":
        shutil.copy2("/var/templates/nginx-puma.png", "app/public")

        sys.stderr.write("Running rails installation.\n")
        subprocess.check_call(["gem", "install",
                               "bundler", "rack", "rails", "rake", "puma"
                              ],
                              env=kwargs["environ"],
                              stderr=sys.stderr,
                              stdout=sys.stderr)

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
    """Render a Jinja2 template into the given file."""
    if not os.path.exists(path):
        template = env.get_template(template)
        with open(path, "w", encoding="utf-8") as f:
            f.write(template.render(**kwargs))


def pwgen(length=128):
    """Generate a secure password."""
    proc = subprocess.Popen(["pwgen", "--secure", "{}".format(length), "1"],
                            stdout=subprocess.PIPE)
    return proc.communicate()[0].decode().strip()


def main(argv):
    # Load global conf
    environ = os.environ

    groupname = environ["GROUPNAME"]

    if environ["CONFIG"] == "Rails":
        environ["GEM_HOME"] = "/var/www/.gem/ruby/2.3.0"
        environ["SECRET_KEY_BASE"] = "{:0128x}".format(random.randrange(16**128))
        with open("/etc/container_environment/SECRET_KEY_BASE", "w+") as f:
            f.write(environ["SECRET_KEY_BASE"])

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
                           "s/mailhub=mail/mailhub=smtp:1025/",
                           "/etc/ssmtp/ssmtp.conf"],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)


    # Create the group
    create_group(groupname)
    p = pwd.getpwnam(groupname)
    uid, gid = p.pw_uid, p.pw_gid
    # Ownership of existing files
    os.chown(wwwdir, uid, gid)
    for root, dirs, files in os.walk(wwwdir):
        for d in dirs:
            os.chown(os.path.join(root, d), uid, gid)
        for f in files:
            os.chown(os.path.join(root, f), uid, gid)
    # Use ACL to set the rights.
    subprocess.check_call(["setfacl", "-R", "-m",
                           "group:{}:rwX".format(groupname),
                           wwwdir],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)
    subprocess.check_call(["setfacl", "-dR", "-m",
                           "group:{}:rwX".format(groupname),
                           wwwdir],
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE)

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
                               "laravel, rails, github, comment")

    if (os.path.exists(students)):
        with open(students, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            # skip headers
            next(reader)
            for student in map(StudentRecord._make, reader):
                # By default the group is the laravel one.
                if environ["CONFIG"] == "Rails":
                    group = student.rails
                else:
                    group = student.laravel

                # Only pick the users of the given group
                if group in (groupname, "admin"):
                    username = formatUserName(student.firstname)
                    create_user(username, groupname, student.classname)
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
        sys.stderr.write("No {} file found.\n".format(students))

    sys.stderr.write("Setup is done.\n")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
