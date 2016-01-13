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
    $ mv app demo
    $ rails new app --database=postgres|mysql
    $ cd app

Add 'puma' the to Gemfile. This will be the default in Rails 5.

    # Use Puma as the web server
    gem 'puma'

Restart the web server:

    $ sudo sv restart puma

And experience the database fail screen. That's good.


### Configure the database.yml file

The database is the named after the username, use them both.

    default: &default
      adapter: postgresql
      encoding: unicode
      pool: 5
      host: postgres
      username: <%= ENV['POSTGRES_USERNAME'] %>
      password: <%= ENV['POSTGRES_PASSWORD'] %>

    development:
      <<: *default
      database: <%= ENV['POSTGRES_USERNAME'] %>_development

    test:
      <<: *default
      database: <%= ENV['POSTGRES_USERNAME'] %>_test

    production:
      <<: *default
      database: <%= ENV['POSTGRES_USERNAME'] %>_production

or if you prefer MySQL:

    default: &default
      adapter: mysql2
      encoding: utf8mb4
      pool: 5
      timeout: 5000
      host: mysql
      database: <%= ENV['MYSQL_USERNAME'] %>
      username: <%= ENV['MYSQL_USERNAME'] %>
      password: <%= ENV['MYSQL_PASSWORD'] %>


### The server

The puma server should be running already, you can restart it this way:

    $ sudo sv restart puma

Idem with nginx.

    $ sudo sv restart nginx

### Differences with Laravel

Instead of Composer, you’ll use Bundler and Ruby Gems.

### Ruby on Rail 5.0.0 beta1

There is a demonstration video from @dhh on
[youtube](https://www.youtube.com/watch?v=n0WUjGkDFS0).

    $ gem install --prerelease rails
    $ rails --version
    Rails 5.0.0.beta1

I've tested it (locally) and it's neat! The websocket will be hard to set up
on the srvz-app machine, sadly.

{% include 'README-footer.md' %}
