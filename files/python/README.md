# README

Welcome aboard!

## Files

`README.md` is this file.

The funny message comes from `~/.bash_profile`.

Feel free to adapt the git configuration in `~/.gitconfig`.

## MySQL

Connect to MySQL (hint: `echo \$PASSWORD`):

```
$ mysql --host $MYSQL_HOST --user $GROUPNAME --password
```

## Postgres

Connect to Postgres:

```
$ psql -h $POSTGRES_HOST -U $GROUPNAME
```

# Python

By default, the system comes with a virtual env and a simple WSGI application.

```
$ cd /var/www/app
$ source venv/bin/activate
(venv)$ python --version
Python 3.6.3
(venv)$ pip list
pip (9.0.1)
pkg-resources (0.0.0)
setuptools (38.2.5)
wheel (0.30.0)
```

The WSGI application is defined in the `wsgi.py` file. WSGI is the protocol between the application server and a Python application. The application server used is called uWSGI. A request is handled by Nginx which delegates it to uWSGI that manages various Python processes running you application.

```
+-------+             +-------+            +--------+
| NGINX | <= socket=> | uWSGI | <= WSGI => | Python |
+-------+             +-------+            +--------+
```

The files:

```
/var/www/
         app/
             public/       # files handled by NGINX
             venv/         # Python Virtual environment
             wsgi.py       # Python WSGI application
         config/
                nginx.conf # NGINX configuration
                uwsgi.ini  # uWSGI configuration
         logs/
              access.log   # NGINX access log
              error.log    # NGINX error log
              uwsgi.log    # uWSGI log
```

You interesting processes that you can reload, stop etc. using `sv` are:

```
$ sudo sv status nginx uwsgi
run: nginx: (pid: 2) ...s
run: uwsgi: (pid: 3) ...s
```

## Creation of a Django application

```
$ cd /var/www/app
$ source venv/bin/activate
(venv) $ pip install Django
Successfully installed Django-2.0 pytz-2017.3
(venv) $ django-admin startproject mysite
(venv) $ cd mysite
```

### Configure uWSGI

Change the `chdir` instruction into `/var/www/conf/uwsgi.ini`

```ini
chdir=/var/www/app/mysite
virtualenv=/var/www/app/venv    # change it if you recreate a venv
module=mysite.wsgi:application
```

Add your host to `mysite/settings.py`

```python
ALLOWED_HOSTS = ['groupname.srvz-webapp.he-arc.ch']
```

Reload uWSGI:

```
$ sudo sv reload uwsgi
```

And open the browser, you should see the _Congratulations!_ message.

### The Polls app

```
(venv) $ python manage.py startapp polls
```

Then follow the [online tutorial](https://docs.djangoproject.com/en/1.10/intro/tutorial01/) which will guide you through the creation of a real application.

### Database configuration

Before running the migrations, we need to configure the database.

#### MySQL

```
(venv) $ pip install mysqlclient
```

```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': os.environ.get('GROUPNAME'),
    'USER': os.environ.get('GROUPNAME', 'root'),
    'PASSWORD': os.environ.get('PASSWORD', ''),
    'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
    'PORT': os.environ.get('MYSQL_PORT', '3306'),
    'OPTIONS': {
      'charset': 'utf8mb4'
    }
  }
}
```

#### Postgres

```
(venv) $ pip install psycopg2
```

```python
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get('GROUPNAME'),
    'USER': os.environ.get('GROUPNAME', 'postgres'),
    'PASSWORD': os.environ.get('PASSWORD', ''),
    'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
    'PORT': os.environ.get('POSTGRES_PORT', '5432')
  }
}
```

#### Migration

```
(venv) $ python manage.py migrate
```

Et voilà.


## Troubleshooting

Do you have a problem or need anything? Send us an issue or come have a chat:

- <https://github.com/HE-Arc/webapp-server/issues>
- <https://gitter.im/HE-Arc/webapp-server>
