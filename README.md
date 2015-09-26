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
Blanc     Yoan       Teacher    admin       greut     -
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

$ scripts/github_keys.py config/students.tsv config/keys/ <github_username> <password_or_key>
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

Warning, the `-p` opens it up to the whole world (`0.0.0.0`).

```shell
$ docker run --name database \
    -e MYSQL_ROOT_PASSWORD=root \
    -v `pwd`/../data:/var/lib/mysql \
    -p 3306:3306 \
    -d mariadb:5.5

$ mysql -u root -p
```

#### Post-setup

Changing MySQL root password because the above value will be passed to each
linked containers.

```shell
$ mysqladmin -h 172.17.0.1 -u root -p'root' password 's3cur3@P45sw0rd'
```

### Create the databases

For each group:

    CREATE USER 'groupname'@'%';"
    SET PASSWORD FOR 'groupname'@'%' = PASSWORD('password');",
    CREATE DATABASE `groupname`
        DEFAULT CHARACTER SET utf8mb4
        DEFAULT COLLATE utf8mb4_unicode_ci;
    GRANT ALL PRIVILEGES ON `groupname`.* TO 'groupname'@'%';
    FLUSH PRIVILEGES;

### Starting the machine!

```shell
$ docker run --name FunkyNinja \
    --env GROUPNAME=FunkyNinja \
    --env MYSQL_DATABASE=FunkyNinja \
    --env MYSQL_USERNAME=FunkyNinja \
    --env MYSQL_PASSWORD=root \
    --hostname funkyninja.labinfo.he-arc.ch \
    --link database:mysql \
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
