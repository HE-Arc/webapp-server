{%- extends "base/README.md" -%}

{#- vim: set ft=jinja: -#}

{% block body %} {{ super() }}

# Ruby on Rails

Most of the stuff required are installed by default as you can see.

```
$ ruby --version
ruby 2.4.0p0 (2016-12-24 revision 57164) [x86_64-linux-gnu]
$ rails --version
Rails 5.0.1
```

## The current application

```
$ cd www/app
$ cat config.ru

so ruby                      such html!
         amazing
  Wow               Great

$ cat Gemfile
source 'http://rubygems.org'

gem 'puma'
gem 'rack'
```

This is a minimal Rack application. Rack is a web server interface so application and web servers can communicate easily. Much like CGI but for the common times.

Let's modify it and restart the application server:

```
$ sed -i 's/Ruby/HE-ARC/' config.ru

$ sudo sv restart puma
# or
$ touch tmp/restart.txt
```

Here, we replaced PHP-FPM with Puma to serve the Ruby application.

```
$ ls ~/www/config
nginx.conf                    # the HTTP server configuration
puma.rb                       # the application server configuration
```

The application will be relaunched every time you modify (or touch) the `config.ru` file.

## Creation of a Ruby on Rails web application

```
$ cd www
# Backup the demo application.
$ mv app demo

$ rails new app --database=postgresql
# or
$ rails new app --database=mysql

$ cd app
# restart the server
$ sudo sv restart puma
```

And experience the connection error (in development) or 404 page (in production). That's good.

## Configure the database.yml file

The database is the named after the username. And the various environments are set in three schemas ($user, production and test). As you'll develop locally, let the development environment set to your local setup and use only the production environment. (See also the staging environment below)

```yaml
default: &default
  adapter: postgresql
  encoding: unicode
  pool: 5
  # Add the following.
  host: postgres
  user: postgres
  password: <%= ENV['PASSWORD'] %>

development:
  <<: *default
  # Not required, because it's the default value.
  database: app_development

test:
  <<: *default
  database: app_test

production:
  <<: *default
  database: <%= ENV['GROUPNAME'] %>
  username: <%= ENV['GROUPNAME'] %>
  password: <%= ENV['PASSWORD'] %>
  schema_earch_path: production
```

or if you prefer MySQL:

```
default: &default
  adapter: mysql2
  encoding: utf8mb4
  pool: 5
  timeout: 5000
  host: mysql
  password: <%= ENV['PASSWORD'] %>
  username: <%= ENV['GROUPNAME'] %>

development:
  database: <%= ENV['GROUPNAME'] %>

test:
  database: <%= ENV['GROUPNAME'] %>_test

production:
  database: <%= ENV['GROUPNAME'] %>_production
```

Yay! You're on Rails!

```
$ touch tmp/restart.txt
```

## Differences with Laravel

Instead of Composer, you'll use Bundler and Ruby Gems.

# Dropping the database

The database cannot be dropped, instead you have to drop the schema and then recreate it. Rake doesn't have a task that do that. In case you're stuck with a broken beyond repair schema do this:

```
$ psql -h postgres -U $GROUPNAME $GROUPNAME
Password for user ...: $PASSWORD

=> \dn
  List of schemas
  ...
=> DROP SCHEMA schemaname CASCADE;
=> CREATE SCHEMA schemaname;
```

That should do it.

# Staging environment

Don't use the development environment on the server because it will mess your configuration up.

The solution is to have a second development environment, let's call it staging.

First, create a new file in `config/environments/`:

```
# staging.rb
require Rails.root.join("config/environments/development")
```

Give it a `secret_key_base` into `config/secrets.yml`.

And finally, configure its database.

```
staging:
  << *default
  database: <%= ENV['GROUPNAME'] %>
  user: <%= ENV['GROUPNAME'] %>
  password: <%= ENV['PASSWORD'] %>
```

It will use the default `schema_search_path`, which is the one named after the owner (`$user`).

Change `www/config/puma.rb` to `staging`, migrate and enjoy.

```
$ RAILS_ENV=staging bin/rake db:migrate
```

## Error messages

If you take a look at the logs when an exception is raised, you'll see an error message regarding the console and a non-authorized ip address. Rails, doesn't allow external users to look at your exceptions by default. Good security practice but maybe not how you prefer to work.

Add your ip address to `staging.rb` this way:

```
Rails.application.configure do
  config.web_console.whitelisted_ips = 'xxx.xxx.xxx.xxx'
end
```

You can also enable a subnet using the CIDR notation.

{% endblock -%}
