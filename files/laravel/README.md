# README

Welcome aboard!

## Files

`README.md` is this file.

The funny message comes from `~/.bash_profile`.

Feel free to adapt the git configuration in `~/.gitconfig`.

# PHP

Composer is installed for your convenience.

```
$ composer --help
```

But you may have to install the laravel-installer.

```
$ composer global require laravel/installer
```

# Laravel tutorial

This is from the [Laravel 5.7 documentation](http://laravel.com/docs/5.7).

## Creating a new project

Here we are creating a project called `blog`

```
$ cd www
$ laravel new blog
$ cd blog
$ sudo setfacl -R -m u:www-data:rwx storage bootstrap/cache
$ sudo setfacl -dR -m g:poweruser:rwx storage bootstrap/cache
```

## Nginx (_engine-X_)

You only have to fix the path into the nginx configuration file to have your application showing up on port 80\. The file is `www/config/nginx.conf`

```
#root /var/www/app;
root /var/www/blog/public;
```

And restart the servers:

```
$ sudo sv restart nginx
```

If you think nginx didn't read the new config (and/or `/var/log/nginx/error.log` is growing) :

```
$ sudo killall nginx
```

Your website should display the laravel default homepage.

### Logs

The server logs are put there in `/var/www/logs`.

The error log will be useful.

```
$ tail /var/www/logs/error.log
```

Check `/var/log/nginx` too! It can grow big, to clear it : `sudo truncate -s0 /var/log/nginx/error.log`


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
        'unix_socket' => env('DB_SOCKET', ''),
        'charset' => 'utf8mb4',
        'collation' => 'utf8mb4_unicode_ci',
        'prefix' => '',
        'prefix_indexes' => true,
        'strict' => true,
        'engine' => null,
    ],
    // ...
],
// ...
```

`env('MYSQL_HOST')` (aka `$_SERVER['MYSQL_HOST']`) is the environment variable containing the host name of the MySQL server. Hence, you don't have to put it in the `.env` file. Keep the `.env` file for you local setup.

## Using Postgres instead of MySQL

You may also want to use Postgres. The configuration is alike and you'all have to change the default key to this one.

```
'default' => env('DB_CONNECTION', 'pgsql'),
```

## Environments

In MySQL, you've got three databases named after your groupname. One could be used for running your tests and the other one for production.

In Postgres, it's similar expect that this is done with three schemas within one database.

# Initializing the models

The models are defined through [migrations](http://laravel.com/docs/5.7/migrations) which enable rollbacks. You should always use them. We will instantiate the default model which creates two tables do deal with users and their password.

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

Laravel comes with some default libraries like Bootstrap and Vue.js. To rebuild them, do the following commands:

```
$ npm install
$ npm run dev # or development
$ npm run prod # or production
```

Although, doing this on the production server is not a good idea. Putting the generated scripts and stylesheets on Git is ok.

# Mixed content issue

Laravel "helper" functions such as [``asset()``](https://laravel.com/docs/5.7/helpers#method-asset) or [``route()``](https://laravel.com/docs/5.7/helpers#method-route) should detect the current protocol (HTTP or HTTPS) and output URLs accordingly. However, when you deploy your application and browse it in HTTPS, you may notice that assets such as JavaScript or CSS are loaded in HTTP. Thus they are blocked for security reasons because your browser considers them as [mixed content](https://developer.mozilla.org/en-US/docs/Web/Security/Mixed_content). So, what's happening here ? Why ``asset()`` and ``route()`` functions do not work correctly ?

## Explanation

This comes from the architecture of the server: any HTTP(S) request targeting a subdomain of ``srvz-webapp.he-arc.ch`` first hits a reverse proxy called [Træfik](https://docs.traefik.io/basics/).
It will parse the requested hostname (``group1.srvz-webapp.he-arc.ch`` or ``group2.srvz-webapp.he-arc.ch`` or ...) and then forward the request to the matching Nginx server (``group1``'s or ``group2``'s or ...).

The mixed content issue comes from here: the [HTTPS connection terminates](https://en.wikipedia.org/wiki/TLS_termination_proxy) between the browser and the reverse proxy ; your proxy "speaks" to your Nginx server in cleartext HTTP. In consequence, your Laravel application will consider that the content was requested in HTTP, which explains why ``asset()`` and ``route()`` functions did not work as expected.

## Solution

The best solution to solve this issue is to use the ``X-Forwarded-Proto`` HTTP header that the reverse proxy set before forwarding the request to your Nginx server. It contains the protocol (HTTP or HTTPS) the client used in the original request.

Laravel contains classes (such as Symfony's ``Request`` class) that are able to check the value of this header and then output correct URLs automatically, but by default it will just ignore it for (again) security reasons because it does not "trust" the proxies and their ``X-Forwarded-*`` HTTP headers.
To change this behavior, we can use the ``TrustProxies`` middleware that Laravel [includes by default since version 5.5](https://laravel-news.com/trusted-proxy).

All you need to do is to set the ``$proxies`` attribute with the addresses of trusted proxies in ``app/Http/Middleware/TrustProxies.php``. The hasty solution is to trust any proxies:

```php
// ...
// Trust any proxies
protected $proxies = '*';
// ...
```

If you want to be more restrictive and only trust the reverse proxy used in the server, you must first obtain its IP address. The easiest way to get it is to read the Nginx access log (if you take a look at it, you will notice that all requests comes from the same IP address, the reverse proxy's one):

```bash
$ # Takes the last line of the Nginx access log and
$ # outputs the "client" IP address, in our case the reverse proxy's
$ tail -n 1 ~/www/logs/nginx_access.log | cut -d ' ' -f 1
172.18.0.6
```
Make sure to run this command yourself and use its output afterwards, the address may be different on your server for any reason whatsoever.

Then, still in ``app/Http/Middleware/TrustProxies.php``:

```php
// ...
// Trust specific proxies
protected $proxies = [
    '172.18.0.6',  // Replace with the address found using the command above
];
// ...
```

That's it, now that Laravel "trusts" the reverse proxy, it will read the value set in the ``X-Forwarded-Proto`` HTTP header. This means it now knows with which protocol the client (your browser) made the request, and will output URLs accordingly.
No more mixed content issue.

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

## Mail

If you want to use the mail service from the local server : <https://webmail.srvz-webapp.he-arc.ch/> you need to configure your application as such.

```
MAIL_DRIVER=mail

# or

MAIL_HOST=smtp
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ADDRESS=noreply@example.org
MAIL_NAME="No Reply"
MAIL_ENCRYPTION=null
```

**NB:** this doesn't allow you to send email outside the local network, all mails will be caught by mailhog. If you want to really put your app in production with real email service, you'll need to config another service such as gmail, mailgun, amazon, etc._
