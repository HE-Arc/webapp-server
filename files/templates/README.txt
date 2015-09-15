{# vim: set ft=jinja: -#}
README
======

Welcome abroad.

Files
-----

Your `www` directory is shared with your group, the rest is not.


MySQL
-----

Connect to MySQL (hint: \`echo \$MYSQL_PASSWORD\`):

$ mysql --user $MYSQL_USERNAME --host $MYSQL_HOSTNAME --password $MYSQL_DATABASE

You may also see how it's currently done in `index.php`.


PHP
---

Composer and Laravel are installed for your convenience.

$ composer --help
$ laravel --help


Laravel tutorial
----------------

This is from the Laravel 5.1 documentation.

Creating a new project
^^^^^^^^^^^^^^^^^^^^^^

Here we are creating a project called `blog`

    $ cd www
    $ laravel new blog
    $ chmod -R 0777 blog/storage
    $ chmod 0777 blog/bootstrap/cache
    $ cp blog/.env.example blog/.env
    $ php artisan key:generate
    $ setuser www-data php artisan serve --host 0.0.0.0


Configuring the database connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Modify the following lines in `blog/.env` (the filename starts with a dot).
You have to comment out the `DB_*` entries as we don't need them here.

    #DB_HOST=localhost
    #DB_DATABASE=homestead
    #DB_USERNAME=homestead
    #DB_PASSWORD=secret

We are gonna read the database configuration from the environement. See
[12factors](http://12factor.net/config).

Modify `blog/config/database.php` as such:

    // ...
    'connections' => [
        // ...
        'mysql' => [
            'driver' => 'mysql',
            'host' => env('DB_HOST', $_SERVER['MYSQL_HOST']),
            'database' => env('DB_DATABASE', $_SERVER['MYSQL_DATABASE']),
            'username' => env('DB_USERNAME', $_SERVER['MYSQL_USERNAME']),
            'password' => env('DB_PASSWORD', $_SERVER['MYSQL_PASSWORD']),
            'charset' => 'utf8', // utf8mb4: if you want emoji
            'collation' => 'utf8_unicode_ci', // utf8mb4_unicode_ci: ditto
            prefix' => '',
            'strict' => false
        ],
        // ...
    ],
    // ...

`$_SERVER['MYSQL_HOST']` is the environment variable containing the host for
the MySQL connection, much more flexible than `.env` files.


Initializing the models
^^^^^^^^^^^^^^^^^^^^^^^

The models are defined through
[migrations](http://laravel.com/docs/5.1/migrations) which enable rollbacks.
You should always use them.

    $ php blog/artistan migrate
    Migration table created successfully.
    Migrated: 2014_10_12_00000_create_users_table
    Migrated: 2014_10_12_10000_create_password_resets_table

This ran the existing migrations.


Nginx
^^^^^

You only have to fix the path into the nginx configuration file to have your
application showing up on port 80. The file is /etc/nginx/sites-availables/{{ groupname }}

    #root /var/www;
    root /var/www/blog/public;

And restart your server:

    $ sudo sv restart nginx

Et voilà!


Tools
-----

Other great tools you might need, one day:

$ ack-grep {{ username }}
$ npm
$ vim
$ screen
$ tmux
$ pip

