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
$ docker build -t greut/webapp-server:base -f docker/base/Dockerfile .
# Laravel container
$ docker build -t greut/webapp-server:laravel -f docker/laravel/Dockerfile .
# Rails container
$ docker build -t greut/webapp-server:rails -f docker/rails/Dockerfile .
```

## Run via docker-compose

A sample YAML file.

```yaml
$GROUPNAME-php:
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

$GROUPNAME-ror:
  image: greut/webapp-server:rails
  environment:
    - GROUPNAME=$GROUPNAME
    - MYSQL_DATABASE=$GROUPNAME
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
  image: redis:latest

memcached:
  image: memcached:latest

postgres:
  image: postgres:latest
  environment:
    - POSTGRES_PASSWORD=root
  volumes:
    - ../data/postgres:/var/lib/postgres/data
  ports:
    - "5432:5432"
mysql:
  image: mariadb:latest
  environment:
    - MYSQL_ROOT_PASSWORD=root
  volumes:
    - ../data/mysql:/var/lib/mysql
  ports:
    - "3306:3306"

mailcatcher:
  image: schickling/mailcatcher
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
$ mysqladmin -h 127.0.0.1 root -p'root' password 's3cur3@P45sw0rd'
```

##### Create the database

For each group:

    CREATE USER 'groupname'@'%';
    SET PASSWORD FOR 'groupname'@'%' = PASSWORD('password');
    CREATE DATABASE `groupname`
        DEFAULT CHARACTER SET utf8mb4
        DEFAULT COLLATE utf8mb4_unicode_ci;
    GRANT ALL PRIVILEGES ON `groupname`.* TO 'groupname'@'%';
    FLUSH PRIVILEGES;

#### PostgreSQL

```shell
$ docker run \
    --name database.postgres \
    -e POSTGRES_PASSWORD=mysecretpassword \
    -v `pwd`/../data/postgresql:/var/lib/postgresql/data \
    -p 5432:5432 \
    -d postgres:9.3
```

##### Post-setup

Changing Postgres password because the above value will be passed to each
linked containers.

```shell
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "ALTER USER postgres WITH PASSWORD 's3cur3@P45sw0rd';"
```

##### Create the role

```shell
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "CREATE ROLE groupname LOGIN PASSWORD 'password' CREATEDB VALID UNTIL 'infinity'"
```

## Updating the machines

See [fabfile.py](fabfile.py).
