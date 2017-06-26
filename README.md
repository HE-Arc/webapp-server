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

### Public keys

To download the public keys, run this python script:

```console
# setup
$ python3 -m venv .
$ . bin/activate
$ pip3 install -r requirements.txt

$ scripts/github_keys.py config/students.tsv config/keys/ <github_username> <password_or_key>
```

The key is a [personal access token](https://github.com/settings/tokens) to avoid being rate limited by the API.

### Docker-compose

Based on the same TSV file, you can generate `docker-compose.yml` file.

```console
$ scripts/team2_compose.py \
    config/students.tsv \
    docker-compose.yml \
    nginx.conf \
    index.html
```

**TODO** `team2_compose.py` was intended for the second round of projects, one for the first one is still needed.

**TODO** the generated docker-composer.yml doesn't take into account the Traefik setup in place.

### Database creation

Reusing the `docker-compose.yml` file, it builds

```console
$ script/bdd.py docker-compose.yml
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
