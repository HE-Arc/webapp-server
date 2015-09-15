# WebApp Server

The setup scripts to create development environments for many groups.

## Requirements

 * Docker
 * Python3 (requests)

## Setup

__TODO__: download the students and the public keys.

### Building the container

```
$ docker build -t greut/webapp-server .
```

### Starting MySQL

```shell
$ docker run --name database -e MYSQL_ROOT_PASSWORD=passwd \
           -v `pwd`/../data:/var/lib/mysql
           -d mariadb:5.5

$ docker inspect --format="{{.NetworkSettings.IPAddress}}" database
172.17.0.1
```

### Starting the machine!

```shell
$ docker run --name abba.labinfo.he-arc.ch \
           --env GROUPNAME=abba \
           --env GITHUB_USER=greut \
           --env GITHUB_KEY=`cat github.key` \
           -h abba.labinfo.he-arc.ch \
           --link database:mysql \
           -v `pwd`/www/abba:/var/www \
           -d greut/webapp-server

$ docker inspect --format="{{.NetworkSettings.IPAddress}}" abba.labinfo.he-arc.ch
```

### Post-setup

Changing MySQL root password (for obvious security reasons):

```shell
$ mysqladmin -h 172.17.0.1 -u root -p'passwd' password 'new-passwd'
```

## TODO

 * monitoring: influxdb, cadvisor and grafana
 * git repositories with gogs?
