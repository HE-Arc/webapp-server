#!/usr/bin/env python3
"""
Setup
-----

Create the environment, users with all the required files.
"""

__author__ = "Yoan Blanc <yoan@dosimple.ch>"
__version__ = "0.6.0"

import re
import os
import csv
import sys
import pwd
import random
import shutil
import hashlib
import subprocess
import unicodedata
import multiprocessing

from collections import namedtuple
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("/var/templates"))
wwwdir = "/var/www"


def passwd(passphrase, algorithm='sha1'):
    """Code borrowed from notebook.auth.security"""
    salt_len = 32
    h = hashlib.new(algorithm)
    salt = ("{0:0%dx}" % salt_len).format(random.getrandbits(4 * salt_len))
    h.update(passphrase.encode("utf-8") + bytearray.fromhex(salt))
    return ':'.join((algorithm, salt, h.hexdigest()))


env.filters['passwd'] = passwd


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

    paths = [("base/bash_profile", ".bash_profile"),
             ("base/gitconfig", ".gitconfig"), ("base/pgpass", ".pgpass")]
    config = kwargs["environ"].get("CONFIG", None)
    if config == "Laravel":
        paths.append(("laravel/README-php.md", "README.md"))
    elif config == "Rails":
        paths.append(("rails/README.md", "README.md"))
    elif config == "Python":
        paths.append(("python/README.md", "README.md"))
    else:
        paths.append(("base/README.md", "README.md"))
    for tpl, dest in paths:
        if not os.path.exists(dest):
            render(tpl, dest, username=username, groupname=groupname, **kwargs)

    # Chmod the postgres configuration
    os.chmod(".pgpass", mode=0o0600)

    # link /var/www to ~/www
    os.symlink(wwwdir, "www")

    # Create .ssh/authorized_keys
    os.mkdir(".ssh")
    os.chmod(".ssh", mode=0o0700)


def create_user(username, groupname, comment):
    """Create a UNIX user (the group must exist beforehand)."""
    groups = ["users"]

    subprocess.check_call(
        [
            "useradd", username, "-c", comment, "--create-home",
            "--no-user-group", "--shell", "/bin/bash", "--groups",
            ",".join(groups)
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)
    subprocess.check_call(
        [
            "usermod", username, "--gid", groupname, "--groups",
            "{},users".format(groupname)
        ],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)
    proc = subprocess.Popen(
        ["chpasswd"],
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
    environ = kwargs["environ"].copy()
    environ["HOME"] = homedir

    paths = []
    dirs = ["config", "logs"]

    if config == "Laravel":
        dirs.append("public")

        paths = (("laravel/public/index.php", "public/index.php"),
                 ("laravel/config/nginx.conf", "config/nginx.conf"))

    elif config == "Rails":
        dirs.append("app/public")
        dirs.append("iruby")
        dirs.append(kwargs["environ"]["GEM_HOME"])

        paths = (("rails/config/nginx.conf", "config/nginx.conf"),
                 ("rails/config/puma.rb", "config/puma.rb"),
                 ("rails/app/Gemfile", "app/Gemfile"),
                 ("rails/iruby/Gemfile", "iruby/Gemfile"),
                 ("rails/iruby/hello-ruby.ipynb", "iruby/hello-ruby.ipynb"),
                 ("rails/iruby/run.sh", "iruby/.run.sh"),
                 ("rails/iruby/jupyter-config.py", "iruby/.jupyter-config.py"),
                 ("rails/app/config.ru", "app/config.ru"))

    elif config == "Python":
        dirs.append("app/public")
        dirs.append("app/venv")
        dirs.append(kwargs["environ"]["PYTHONUSERBASE"])

        paths = (("python/config/nginx.conf", "config/nginx.conf"),
                 ("python/config/uwsgi.ini", "config/uwsgi.ini"),
                 ("python/app/wsgi.py", "app/wsgi.py"))

    else:
        dirs.append("public")

        paths = (("base/config/nginx.conf", "config/nginx.conf"),
                 ("base/public/index.html", "public/index.html"))

    for p in dirs:
        if not os.path.exists(p):
            os.makedirs(p)

    for tpl, dest in paths:
        if not os.path.exists(dest):
            render(tpl, dest, groupname=groupname, **kwargs)

    def check_call(command, env, stderr=sys.stderr, stdout=sys.stderr):
        subprocess.check_call(command, env=env, stderr=stderr, stdout=stdout)

    if config == "Laravel":
        sys.stderr.write("Running composer global require laravel/installer\n")
        check_call(
            ["composer", "global", "require", "laravel/installer=~1.3"],
            env=kwargs["environ"])

    elif config == "Rails":
        shutil.copy2("/var/templates/rails/app/public/nginx-puma.png",
                     "app/public")

        sys.stderr.write("Running rails installation.\n")
        check_call(
            ["gem", "install", "bundler", "rack", "rails", "rake", "puma"],
            env=kwargs["environ"])
        os.chdir('app')
        check_call(
            ["{0}/bin/bundler".format(environ["GEM_HOME"]), "install"],
            env=kwargs["environ"])
        os.chdir(homedir)

        os.chdir('iruby')
        os.chmod('.run.sh', mode=0o0775)
        sys.stderr.write("Running jupyter/iruby installation.\n")
        check_call(["python3", "-m", "venv", ".venv"], env=kwargs["environ"])
        check_call(
            [
                ".venv/bin/pip", "--no-cache-dir", "install", "-U", "pip",
                "jupyter[notebook]"
            ],
            env=kwargs["environ"])
        check_call(
            ["{0}/bin/bundler".format(environ["GEM_HOME"]), "install"],
            env=kwargs["environ"])
        os.chdir(homedir)

    elif config == "Python":
        shutil.copy2("/var/templates/python/app/public/nginx-uwsgi.png",
                     "app/public")

        sys.stderr.write("Running uwsgi installation.\n")
        check_call(
            ["python3", "-m", "virtualenv", "-p", "python3", "app/venv"],
            env=kwargs["environ"])
        check_call(
            ["app/venv/bin/pip", "--no-cache-dir", "install", "-U", "pip"],
            env=kwargs["environ"])

    return homedir, uid, gid


def create_group(groupname):
    """Create the system user named after the group."""
    subprocess.check_call(
        [
            "useradd", groupname, "-c", "GROUP", "--no-create-home",
            "--home-dir", wwwdir, "--user-group", "--system"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    subprocess.check_call(
        ["usermod", "--lock", groupname],
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
    proc = subprocess.Popen(
        ["pwgen", "--secure", "{}".format(length), "1"],
        stdout=subprocess.PIPE)
    return proc.communicate()[0].decode().strip()


def main(argv):
    # Load global conf
    environ = os.environ

    groupname = environ["GROUPNAME"]
    config = environ["CONFIG"]

    # Global environment "variables"
    environ["MYSQL_HOST"] = "mysql"
    environ["MYSQL_PORT"] = "3306"
    environ["POSTGRES_HOST"] = "postgres"
    environ["POSTGRES_PORT"] = "5432"
    environ["REDIS_HOST"] = "redis"
    environ["REDIS_PORT"] = "6379"
    environ["SMTP_HOST"] = "smtp"
    environ["SMTP_PORT"] = "1025"

    if config == "Laravel":
        environ["COMPOSER_HOME"] = "/var/www/.composer"
    elif config == "Rails":
        environ["GEM_HOME"] = "/var/www/.gem/ruby/2.3.0"
        environ["SECRET_KEY_BASE"] = "{:0128x}".format(
            random.randrange(16**128))
    elif config == "Python":
        environ["PYTHONUSERBASE"] = "/var/www/.local"
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

    # Test if the group exists already
    try:
        p = pwd.getpwnam(groupname)
        sys.stderr.write("Setup already done!\n")
        return 0
    except KeyError:
        pass

    # Configure SSMTP
    subprocess.check_call(
        [
            "sed", "-i", "s/mailhub=mail/mailhub=smtp:1025/",
            "/etc/ssmtp/ssmtp.conf"
        ],
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
    subprocess.check_call(
        ["setfacl", "-R", "-m", "group:{}:rwX".format(groupname), wwwdir],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    subprocess.check_call(
        ["setfacl", "-dR", "-m", "group:{}:rwX".format(groupname), wwwdir],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    # Init the group files
    p = multiprocessing.Process(
        target=init_group, args=(groupname, ), kwargs=dict(environ=environ))
    p.start()
    p.join()

    # symlink the server config
    os.symlink("/var/www/config/nginx.conf",
               "/etc/nginx/sites-enabled/{}".format(groupname))

    # Create users
    students = "/root/config/students.tsv"
    StudentRecord = namedtuple(
        "StudentRecord", "lastname, firstname, email, classname, github, "
        "image1, team1, image2, team2, comment, week")

    if (os.path.exists(students)):
        with open(students, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            # skip headers
            next(reader)
            for student in map(StudentRecord._make, reader):

                if 'LONE_WOLF' not in environ:
                    groups = {student.team1, student.team2}
                else:
                    # '.' is bad for databases name.
                    groups = {student.email.replace('.', '_')}

                # Only pick the users of the given group (or admin)
                if not groups.isdisjoint((groupname, "admin")):
                    username = formatUserName(student.firstname)
                    create_user(username, groupname, student.classname)
                    p = multiprocessing.Process(
                        target=init_user,
                        args=(username, groupname),
                        kwargs=dict(
                            environ=environ, **student._asdict()))
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
