{# vim: set ft=jinja: -#}

{%- extends "base/README.md" -%}

{% block body %} {{ super() }}

You may also see how it's currently done in `index.php`.

# PHP

Composer and Laravel are installed for your convenience.

```
$ composer --help
$ laravel --help
```

# Laravel tutorial

This is from the [Laravel 5.3 documentation](http://laravel.com/docs/5.3).

## Creating a new project

Here we are creating a project called `blog`

```
$ cd www
$ laravel new blog
$ cd blog
$ sudo setfacl -R -m u:www-data:rwx storage bootstrap/cache
$ sudo setfacl -dR -m g:{{groupname}}:rwx storage bootstrap/cache
```

## Nginx (_engine-X_)

You only have to fix the path into the nginx configuration file to have your application showing up on port 80\. The file is `www/config/nginx.conf`

```
#root /var/www/public;
root /var/www/blog/public;
```

And restart the servers:

```
$ sudo sv restart nginx
```

Your website should display the laravel default homepage.

### Logs

The server logs are put there in `/var/www/logs`.

The error log will be useful.

```
$ tail /var/www/logs/error.log
```

## Configuring the database connection

We are gonna read the database configuration from the environment. See [12factors](http://12factor.net/config).

Modify `blog/config/database.php` as such:

```
// ...
'connections' => [
    // ...
    'mysql' => [
        'driver' => 'mysql',
        'host' => env('MYSQL_HOST', env('DB_HOST', 'localhost')),
        'port' => env('MYSQL_PORT', env('DB_PORT', '3306')),
        'database' => env('GROUPNAME', env('DB_DATABASE', 'forge')),
        'username' => env('GROUPNAME', env('DB_USERNAME', 'forge')),
        'password' => env('PASSWORD', env('DB_PASSWORD', '')),
        'charset' => 'utf8mb4',
        'collation' => 'utf8mb4_unicode_ci',
        'prefix' => '',
        'strict' => false
    ],
    // ...
],
// ...
```

`env('MYSQL_HOST') (or`$_SERVER['MYSQL_HOST']`) is the environment variable containing the host for the MySQL connection. It's much more flexible than`.env`files. Keep the`.env` file for you local setup.

What is `utf8mb4`? See: <https://mathiasbynens.be/notes/mysql-utf8mb4>

## Using Postgres instead of MySQL

You may also want to use Postgresql. The configuration is alike but you'all have to change the default key to this one.

```
'default' => env('DB_CONNECTION', 'pgsql'),
```

## Environments

In MySQL, you've got three databases named after your groupname. One could be used for running your tests and the other one for production.

In Postgres, it's similar expect that this is done with three schemas within one database.

# Initializing the models

The models are defined through [migrations](http://laravel.com/docs/5.1/migrations) which enable rollbacks. You should always use them. We will instantiate the default model which creates two tables do deal with users and their password.

The default model was set for utf8 and not utf8mb4, so we have to tweak it a little bit. Open `blog/database/migrations/2014_10_12_000000_create_users_table.php`

```
//$table->string('email')->unique();
$table->string('email', 191)->unique();
```

Now, we are ready to run the migrations:

```
$ php blog/artistan migrate
Migration table created successfully.
Migrated: 2014_10_12_00000_create_users_table
Migrated: 2014_10_12_10000_create_password_resets_table
```

Et voilà!

```
echo "SHOW TABLES" | mysql -u $GROUPNAME -h mysql -p $GROUPNAME
Enter password:
Tables_in_<GROUPNAME>
migrations
password_resets
users
```

# JavaScript and CSS

Laravel comes with some default libraries like Bootstrap. To rebuild them, do the following commands:

```
$ npm install
$ gulp
$ gulp --production
```

Although, doing this on the production server is not a good idea. Putting the generated scripts and stylesheets on Git is ok.

# Advanced topics

Run them at your own risks!

## Queue

Create the following script: /etc/service/laravel-queue-worker/run

```
#!/bin/sh
set -xe
cd /var/www/<app>
exec 2>&1
exec chpst -uwww-data php artisan queue:work
```

## WebSocket

It's doable to set up Laravel Echo and Laravel Echo Server but it can be quite tricky.

```
$ npm install --save-dev laravel-echo pusher-js
$ npm install --save laravel-echo-server
```

Configuration for the Laravel Echo Server:

```
"databaseConfig": {"redis": {"host": "redis"}}
```

Some scripts I've used successfully with runit so far.

```
#!/bin/sh
set -xe
cd /var/www/<app>
exec 2>&1
exec chpst -uwww-data node_modules/.bin/laravel-echo-server start
```

### Hard part

The hard part is that we only have ports 80 and 443 available to us. Hence, we must tweak the nginx configuration to forward any calls made to `/socket.io` to the node.js backend.

If you want to go this route, ping me first.

{% endblock -%}
