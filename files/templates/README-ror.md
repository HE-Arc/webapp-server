{# vim: set ft=jinja: -#}
# README

Here we are again!

## Ruby on Rails

Most of the stuff required are installed by default as you can see.

    $ ruby --version
    ruby 2.2.3p173 (2015-08-18) [x86_64-linux]
    $ rails --version
    Rails 4.2.5

### The current application

    $ cd www/app
    $ cat config.ru

    so ruby                      such html!
             amazing
      Wow               Great

    $ cat Gemfile
    source 'http://rubygems.org'

    gem 'puma'
    gem 'rack'

This is a minimal Rack application. Rack is a web server interface so
application and web servers can communicate easily. Much like CGI but for the
common times.

Let's modify it and restart the application server:

    $ sed -i 's/Ruby/HE-ARC/' config.ru
    $ sudo sv restart puma

Here we replaced PHP-FPM with Puma to serve the Ruby application.

    $ ls ~/www/config
    nginx.conf                    # the HTTP server configuration
    puma.rb                       # the application server configuration
    env                           # environment variables used by puma

The application will be relaunched every time you modify (or touch) the
`config.ru` file.

### Creation of a Ruby on Rails web application

    $ cd www
    # Backup the demo application.
    $ mv app demo

    $ rails new app --database=postgresql
    # or
    $ rails new app --database=mysql

    $ cd app

Add 'puma' the to Gemfile. This will be the default in Rails 5.

    # Use Puma as the web server
    gem 'puma'

Install puma and restart the web server:

    $ bundle
    $ sudo sv restart puma

And experience the database fail screen. That's good.


### Configure the database.yml file

The database is the named after the username. And the various environments are
set in three schemas ($user, production and test). As you'll develop locally,
let the development environment set to your local setup and use only the
production environment. (See also the staging environment below)

    default: &default
      adapter: postgresql
      encoding: unicode
      pool: 5
      # Add the following.
      host: postgres
      user: postgres
      password: <%= ENV['POSTGRES_ENV_POSTGRES_PASSWORD'] %>

    development:
      <<: *default
      # Not required, because it's the default value.
      database: app_development

    test:
      <<: *default
      database: app_test

    production:
      <<: *default
      database: <%= ENV['POSTGRES_USERNAME'] %>
      username: <%= ENV['POSTGRES_USERNAME'] %>
      password: <%= ENV['POSTGRES_PASSWORD'] %>
      schema_earch_path: production

or if you prefer MySQL:

    default: &default
      adapter: mysql2
      encoding: utf8mb4
      pool: 5
      timeout: 5000
      host: mysql
      password: <%= ENV['MYSQL_PASSWORD'] %>
      username: <%= ENV['MYSQL_USERNAME'] %>

    development:
      database: <%= ENV['MYSQL_USERNAME'] %>

    test:
      database: <%= ENV['MYSQL_USERNAME'] %>_test

    production:
      database: <%= ENV['MYSQL_USERNAME'] %>_production


### The server

The puma server should be running already, you can restart it this way:

    $ sudo sv restart puma

Idem with nginx.

    $ sudo sv restart nginx

You should get the "Welcome abroad" screen now.

### Differences with Laravel

Instead of Composer, you’ll use Bundler and Ruby Gems.

### Ruby on Rail 5.0.0 beta1

There is a demonstration video from @dhh on
[youtube](https://www.youtube.com/watch?v=n0WUjGkDFS0).

Before installing rails 5, uninstall the previous rails version.

    $ gem install --prerelease rails
    $ rails --version
    Rails 5.0.0.beta1

I've tested it (locally) and it's neat! The websocket will be hard to set up
on the srvz-app machine, sadly.

## Dropping the database

The database cannot be dropped, instead you have to drop the schema and then
recreate it. Rake doesn't have a task that do that. In case you're stuck with
a broken beyond repair schema do this:

    $ psql -h postgres -U $POSTGRES_USERNAME $POSTGRES_USERNAME
    Password for user ...: $POSTGRES_PASSWORD

    => \dn
      List of schemas
      ...
    => DROP SCHEMA schemaname CASCADE;
    => CREATE SCHEMA schemaname;

That should do it.

## Staging environment

Don't use the development environment on the server because it will mess your
configuration up.

The solution is to have a second development environment, let's call it staging.

First, create a new file in `config/environments/`:

    # staging.rb
    require Rails.root.join("config/environments/development")

Give it a `secret_key_base` into `config/secrets.yml`.

And finally, configure its database.

    staging:
      << *default
      database: <%= ENV['POSTGRES_USERNAME'] %>
      user: <%= ENV['POSTGRES_USERNAME'] %>
      password: <%= ENV['POSTGRES_PASSWORD'] %>

It will use the default `schema_search_path`, which is the one named after the
owner (`$user`).

Change `www/config/puma.rb` to `staging`, migrate and enjoy.

    $ RAILS_ENV=staging bin/rake db:migrate

### Error messages

If you take a look at the logs when an exception is raised, you'll see an error
message regarding the console and a non-authorized ip address. Rails, doesn't
allow external users to look at your exceptions by default. Good security
practice but maybe not how you prefer to work.

Add your ip address to `staging.rb` this way:

    Rails.application.configure do
      config.web_console.whitelisted_ips = 'xxx.xxx.xxx.xxx'
    end

You can also enable a subnet using the CIDR notation.


{% include 'README-footer.md' %}
