# WebApp Server

The setup scripts to create development environments for many groups.

## Requirements

 * Docker
 * Python3 (pip, virtualenv or requests)

## Setup

### Students

The configuration is done via a TSV file (`config/students.tsv`). Here is its
format:

```csv
Lastname  Firstname  Classname  Groupname   GitHub    Comment
Bon       Jean       INF3       FunkyNinja  jeanjean  -
Blanc     Yoan       -          admin       greut     Teacher
...
```

This is how this file is used:

* *Lastname* no particular usage
* *Firstname* becomes the username
* *Classname* no particular usage
* *Groupname* will be the name of the vm and identify a container
* *GitHub* to download the SSH public keys
* *Comment* no particular usage

### Public keys

To download the public keys, run this python script:

```shell
# setup
$ virtualenv3 .
$ . bin/activate
$ pip3 install requests

$ python scripts/github_keys.py config/students.tsv files/keys/ <github_username> <password_or_key>
```

The key is a [personal access token](https://github.com/settings/tokens) to
avoid being rate limited by the API.

### Building the container

This step is no required as this container is [publicly
available](https://hub.docker.com/r/greut/webapp-server/).

```
$ docker build -t greut/webapp-server .
```

### Starting MySQL

```shell
$ docker run --name database -e MYSQL_ROOT_PASSWORD=root \
           -v `pwd`/../data:/var/lib/mysql
           -d mariadb:5.5

$ docker inspect --format="{{.NetworkSettings.IPAddress}}" database
172.17.0.1
```

### Starting the machine!

```shell
$ docker run --name FunkyNinja \
           --env GROUPNAME=FunkyNinja \
           --hostname funkyninja.labinfo.he-arc.ch \
           --link database:mysql \
           -v `pwd`/.../www/abba:/var/www \
           -d greut/webapp-server

$ docker inspect --format="{{.NetworkSettings.IPAddress}}" FunkyNinja
```

### Post-setup

Changing MySQL root password (for obvious security reasons):

```shell
$ mysqladmin -h 172.17.0.1 -u root -p'root' password 's3cur3@P45sw0rd'
```

## TODO

 * monitoring: influxdb, cadvisor and grafana
 * git repositories with gogs?
