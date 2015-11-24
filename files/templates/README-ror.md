{# vim: set ft=jinja: -#}
# README

Here we are again!

## Ruby on Rails

Most of the stuff required are installed by default as you can see.

    $ ruby --version
    ruby 2.2.1p85 (2015-02-26 revision 49769) [x86_64-linux]
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

    gem 'rack'

This is a minimal Rack application. Rack is a web server interface so
application and web servers can communicate easily. Much like CGI but for the
common times.

Let's modify it.

    $ sed -i 's/Ruby/HE-ARC/' config.ru

Here we replaced PHP-FPM with uWSGI to serve the Ruby application.

    $ ls ~/www/config
    nginx.conf                    # the HTTP server configuration
    uwsgi.ini                     # the Rack server configuration

The application will be relaunched every time you modify (or touch) the
`config.ru` file.

### Creation of a Ruby on Rails web application

    $ cd www/app
    $ rm -r .
    $ rails new . --database=postgres|mysql
    $ bundle --deployment  # required on the server only.

### Configure the database.yml file

    development:
      <<: *default
      adapter: postgresql
      encoding: unicode
      pool: 5
      timeout: 5000
      host: <%= ENV['POSTGRES_HOST'] %>
      port: <%= ENV['POSTGRES_PORT'] %>
      database: <%= ENV['POSTGRES_USERNAME'] %>
      username: <%= ENV['POSTGRES_USERNAME'] %>
      password: <%= ENV['POSTGRES_PASSWORD'] %>

or if you prefer MySQL:

    development:
      <<: *default
      adapter: mysql2
      encoding: utf8mb4
      pool: 5
      timeout: 5000
      host: <%= ENV['MYSQL_HOST'] %>
      port: <%= ENV['MYSQL_PORT'] %>
      database: <%= ENV['MYSQL_DATABASE'] %>
      username: <%= ENV['MYSQL_USERNAME'] %>
      password: <%= ENV['MYSQL_PASSWORD'] %>


### Run the migrations.

    $ export RAILS_ENV=development
    $ rake db:create  # for Postgresql only
    $ rake db:migrate


### Running the server

Nothing to see here! It should work as is.

### Differences with Laravel

Instead of Composer, you’ll use Bundler and Ruby Gems.

### Installing global gems

If you wish to install extra ruby gems globally, use rvmsudo:

    $ rvmsudo gem install devise


{% include 'README-footer.md' -%}
