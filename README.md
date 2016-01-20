# WebApp Server

The setup scripts to create development environments for many groups.

## Requirements

 * Docker
 * Python3 (pip, virtualenv or requests)
 * Python2 for [Fabric](http://docs.fabfile.org/)

## Setup

### Students

The configuration is done via a TSV file (`config/students.tsv`). Here is its
format:

```csv
Lastname  Firstname  Email                 Classname  Groupname   GitHub    Comment
Bon       Jean       jean.bon@example.org  INF3       FunkyNinja  jeanjean  -
Blanc     Yoan       yoan@dosimple.ch      Teacher    admin       greut     -
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
$ pip3 install -r requirements.txt

$ scripts/github_keys.py config/students.tsv config/keys/ <github_username> <password_or_key>
```

The key is a [personal access token](https://github.com/settings/tokens) to
avoid being rate limited by the API.

## Containers

If you don't want to use the [publicly available
containers](https://hub.docker.com/r/greut/webapp-server/).

```
# Base container
$ docker build -t greut/webapp-server:latest -f docker/base/Dockerfile .
# Laravel container
$ docker build -t greut/webapp-server:laravel -f docker/laravel/Dockerfile .
# Rails container
$ docker build -t greut/webapp-server:rails -f docker/rails/Dockerfile .
```

## Run via docker-compose

A sample YAML file.

```yaml
$GROUPNAME_php:
  image: greut/webapp-server:laravel
  environment:
    - GROUPNAME=$GROUPNAME
    - MYSQL_DATABASE=$GROUPNAME
    - MYSQL_USERNAME=$GROUPNAME
    - MYSQL_PASSWORD=$GROUPNAME
    - POSTGRES_DATABASE=$GROUPNAME
    - POSTGRES_USERNAME=$GROUPNAME
    - POSTGRES_PASSWORD=$GROUPNAME
  hostname: $GROUPNAME-php
  domainname: srvz-webapp.he-arc.ch
  volumes:
    - ../www/$GROUPNAME:/var/www
    - ./config:/root/config:ro
    - ./files/templates:/tmp/templates:ro
  links:
    - postgres:postgres
    - mysql:mysql
    - redis:redis
    - memcached:memcached
    - mailcatcher:mailcatcher
  ports:
    - "2200:22"
    - "8000:80"

$GROUPNAME_ror:
  image: greut/webapp-server:rails
  environment:
    - GROUPNAME=$GROUPNAME
    - MYSQL_USERNAME=$GROUPNAME
    - MYSQL_PASSWORD=$GROUPNAME
    - POSTGRES_USERNAME=$GROUPNAME
    - POSTGRES_PASSWORD=$GROUPNAME
  hostname: $GROUPNAME-ror
  domainname: srvz-webapp.he-arc.ch
  volumes:
    - ../www/$GROUPNAME:/var/www
    - ./config:/root/config:ro
    - ./files/templates:/var/templates:ro
  links:
    - postgres:postgres
    - mysql:mysql
    - redis:redis
    - memcached:memcached
    - mailcatcher:mailcatcher
  ports:
    - "2001:22"
    - "8001:80"

redis:
  image: redis:3.0

memcached:
  image: memcached:1.4

postgres:
  image: postgres:9.5
  environment:
    - POSTGRES_PASSWORD=root
  volumes_from:
    - data
  ports:
    - "5432:5432"

mysql:
  image: mysql:5.6
  environment:
    - MYSQL_ROOT_PASSWORD=root
  volumes_from:
    - data
  ports:
    - "3306:3306"

mailcatcher:
  image: mailhog/mailhog:latest
  ports:
    - "8025:8025"

data:
  image: busybox:1.24
  volumes:
    - /var/lib/postgresql/data
    - /var/lib/mysql
```

Run the container(s)

```shell
docker-compose up -d
```

### Databases

The databases are open the external world, hence we must modify the super admin
password. Setting up a good one during the startup won't be as effective as it
will be visible from within the containers anyway.

#### MySQL

##### Post-setup

Changing MySQL root password because the above value will be passed to each
linked containers.

```shell
$ mysqladmin -h 127.0.0.1 -u root -p'root' password 's3cur3@P45sw0rd'
```

#### PostgreSQL

Changing Postgres password because the above value will be passed to each
linked containers.

```shell
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "ALTER USER postgres WITH PASSWORD 's3cur3@P45sw0rd';"
```

#### Creating the roles and users

Use the script bdd.py to create the proper databases and roles.

    $ python3 scripts/bdd.py config/bdd.csv

Where the csv file contains key values of this type:

    groupname;password

`pwgen` is a great way to build good passwords.

## Updating the machines

See [fabfile.py](fabfile.py).


## Troubleshooting with docker-compose

COMPOSE_API_VERSION=1.18
