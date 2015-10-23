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

### Building the containers

This step is no required as this container is [publicly
available](https://hub.docker.com/r/greut/webapp-server/).

```
# Base container
$ docker build -t greut/webapp-server:latest -f docker/base/Dockerfile .
# Laravel container
$ docker build -t greut/webapp-server:laravel -f docker/laravel/Dockerfile .
# Rails container
$ docker build -t greut/webapp-server:rails -f docker/rails/Dockerfile .
```

### Databases

#### Starting MySQL

Warning, the `-p` opens it up to the whole world (`0.0.0.0`).

```shell
$ docker run \
    --name database.mysql \
    -e MYSQL_ROOT_PASSWORD=root \
    -v `pwd`/../data/mysql:/var/lib/mysql \
    -p 3306:3306 \
    -d mariadb:5.5

$ mysql -u root -h 127.0.0.1 -p
```

##### Post-setup

Changing MySQL root password because the above value will be passed to each
linked containers.

```shell
$ mysqladmin -h 127.0.0.1 root -p'root' password 's3cur3@P45sw0rd'
```

#### Create the databases

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

#### Create the databases

```shell
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "CREATE ROLE groupname LOGIN PASSWORD 'password' CREATEDB VALID UNTIL 'infinity'"
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "CREATE DATABASE groupname WITH OWNER=groupname ENCODING='UTF-8'"
```

### Starting the machine!

#### Laravel

```shell
$ docker run --name FunkyNinja \
    --env GROUPNAME=FunkyNinja \
    --env MYSQL_DATABASE=FunkyNinja \
    --env MYSQL_USERNAME=FunkyNinja \
    --env MYSQL_PASSWORD=root \
    --hostname funkyninja.labinfo.he-arc.ch \
    --link database.mysql:mysql \
    --link database.postgresql:postgresql \
    -v `pwd`/.../www/FunkyNinja:/var/www \
    -v `pwd`/config:/root/config:ro \
    -p 2201:22 \
    -p 127.0.0.1:8001:80 \
    -d greut/webapp-server

$ ssh -p 2201 you@localhost
```



## Updating composer and laravel

```shell
$ export COMPOSER_HOME=`pwd`/files/composer
$ php files/composer.phar global update
$ php files/composer.phar global info -iN
guzzlehttp/guzzle
guzzlehttp/ringphp
guzzlehttp/streams
laravel/installer
react/promise
symfony/console
symfony/process
```

## Updating the machines

See [fabfile.py](fabfile.py).

## TODO

* monitoring
