# WebApp Server

[![Join the chat at https://gitter.im/HE-Arc/webapp-server](https://badges.gitter.im/HE-Arc/webapp-server.svg)](https://gitter.im/HE-Arc/webapp-server)

- [![](https://images.microbadger.com/badges/image/hearcch/webapp-server.svg)](https://microbadger.com/images/hearcch/webapp-server) [![](https://images.microbadger.com/badges/version/hearcch/webapp-server.svg)](https://microbadger.com/images/hearcch/webapp-server)

- [![](https://images.microbadger.com/badges/image/hearcch/webapp-server:laravel.svg)](https://microbadger.com/images/hearcch/webapp-server:laravel) [![](https://images.microbadger.com/badges/version/hearcch/webapp-server:laravel.svg)](https://microbadger.com/images/hearcch/webapp-server:laravel)

- [![](https://images.microbadger.com/badges/image/hearcch/webapp-server:python.svg)](https://microbadger.com/images/hearcch/webapp-server:python) [![](https://images.microbadger.com/badges/version/hearcch/webapp-server:python.svg)](https://microbadger.com/images/hearcch/webapp-server:python)

- [![](https://images.microbadger.com/badges/image/hearcch/webapp-server:rails.svg)](https://microbadger.com/images/hearcch/webapp-server:rails) [![](https://images.microbadger.com/badges/version/hearcch/webapp-server:rails.svg)](https://microbadger.com/images/hearcch/webapp-server:rails)

The setup scripts to create development environments for many groups.

## Requirements

- Docker >1.13
- Python 3 (pip & venv)
- libyaml-dev

## Setup

### Students

The configuration is done via a TSV file (`config/students.tsv`). Here is its format:

Lastname | Firstname | Email                | Group   | Github   | Image1  | Team1  | Image2 | Team2 | Comment
-------- | --------- | -------------------- | ------- | -------- | ------- | ------ | ------ | ----- | -------
Bon      | Jean      | jean.bon@example.org | INF3    | jeanjean | Laravel | ninjas | Rails  | funky | -
Blanc    | Yoan      | yoan.blanc@he-arc.ch | Teacher | greut    | Laravel | admin  | Python | admin | -

This is how this file is used:

- _Lastname_ no particular usage
- _Firstname_ becomes the username
- _Email_ no particular usage
- _Group_ no particular usage
- _Github_ identifier to download the SSH public keys
- _ImageX_ stores the information of which container to use
- _TeamX_ will be the name of the virtual host and identify a container
- _Comment_ no particular usage

### Setup

The scripts require `docker-compose` as well as other dependencies.

```console
$ python3 -m venv .
$ . bin/activate
(webapp-server)$ pip3 install -r requirements.txt
```

### Docker-compose

Based on the TSV file, you can generate a Docker Compose YAML file.

```console
$ scripts/make_compose.py eatapp \
    < students.tsv \
    > teams/eatapp-compose.yml
```

Then adapt the port number, and run it.

```console
$ docker-compose -f teams/eatapp-compose.yml up
```

### Database creation

Reusing the `docker-compose.yml` file, we create the databases.

```console
$ script/bdd.py < teams/eatapp-compose.yml
```

## Containers

If you don't want to use the [publicly available containers](https://hub.docker.com/r/hearcch/webapp-server/), you can build them yourself.

```
# Base container
$ make base
# Laravel container
$ make laravel
# Python container
$ make python
# Rails container
$ make rails
```

## Run via docker-compose

Create a `docker-compose.yml` file base on the sample one.

Run the container(s)

```console
# create the shared network
$ docker network create --driver=bridge webapp-net

# running the central services
$ docker-compose up -d

# running "a" project
$ docker-compose -f examples/base.yml up -d
```

- Traefik control dashboard runs on port 8080.
- Portainer control dashboard runs on port 9000. The admin password must be set upon boot!

### Databases

The databases are open the external world, hence we must modify the super admin password. Setting up a good one during the startup won't be as effective as it will be visible from within the containers anyway.

#### MySQL

Change the password either in the `docker-compose.yml` file or afterwards this way.

```console
$ mysql -h 127.0.0.1 -u root -proot
> SET PASSWORD FOR 'root'@'%' = PASSWORD('s3cur3@P45sw0rd');
```

#### PostgreSQL

Change the password either in the `docker-compose.yml` file or afterwards this way.

```console
$ psql -h 127.0.0.1 \
    -U postgres \
    -c "ALTER USER postgres WITH PASSWORD 's3cur3@P45sw0rd';"
```

## Standalone setup

Below is a sample of a simple PHP machine with a MySQL instance. The default
environment variable can be overridden (see `scripts/boot.sh`)

```yml
version: "3"

services:
  web:
    image: hearcch/webapp-server:laravel
    ports:
      - "8080:80"
      - "2222:22"
    environment:
      - GROUPNAME=test
      - PASSWORD=test
      - SSH_KEYS=greut
    volumes:
      - web:/var/www
    depends_on:
      - mysql

  mysql:
    image: mysql:5.7
    ports:
      - "3306:3306"
    environment:
      - MYSQL_DATABASE=test
      - MYSQL_USER=test
      - MYSQL_PASSWORD=test
      - MYSQL_RANDOM_ROOT_PASSWORD=1
    volumes:
      - mysql:/var/lib/mysql

volumes:
  web:
  mysql:
```

The login using your github SSH key.

```
$ ssh -p 2222 poweruser@127.0.0.1
```

### Volumes and Windows

On non-UNIX filesystem, it's okay to mount a local folder a the `/var/www` volume. However, on Windows, don't do it and mount the container volume on the machine using SFTP(e.g. <http://www.sftpnetdrive.com/>)
