"""
Fabric configuration to manage to web servers.

Roles:

    $ cat config/roles.json
    {"www": ["server1.he-arc.ch", "server2.he-arc.ch:2222"]}

Simple usage:

    $ fab -H server1.he-arc.ch uptime

Usage with roles:

    $ fab -R www uptime
    $ fab -R www upgrade
"""

import json
import os.path

from fabric.api import env, run, sudo, put


if os.path.exists("config/roles.json"):
    with open("config/roles.json") as f:
        env.roledefs = json.load(f)


def uptime():
    """Display the uptime."""
    run("uptime")


def upgrade():
    """Update, upgrade and autoremove"""
    sudo("apt-get update -q")
    sudo("apt-get upgrade -q -y")
    sudo("apt-get autoremove -y")


def install_ssmtp():
    """sSMTP is useful to send some emails around."""
    sudo("apt-get install ssmtp -q -y")
    sudo(r"sed -i 's/mailhub=mail/mailhub=srvz-webapp.he-arc.ch:1025/' /etc/ssmtp/ssmtp.conf")
    sudo(r"sed -i 's/#FromLineOverride=Yes/FromLineOverride=Yes/' /etc/ssmtp/ssmtp.conf")


def reload():
    """Restart php5-fpm and nginx."""
    sudo("sv restart php5-fpm")
    sudo("sv restart nginx")


def logrotate():
    """Configure logrotate"""
    sudo(r"sed -i 's/^su root syslog/su root adm/' /etc/logrotate.conf")
    put("files/templates/*.logrotate", "/etc/logrotate.d", use_sudo=True)
    sudo("chown root:root /etc/logrotate.d/*")

def php5mcrypt():
    """Enable php5-mcrypt."""
    sudo("php5enmod mcrypt")
