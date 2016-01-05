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

Let's modify it.

    $ sed -i 's/Ruby/HE-ARC/' config.ru

Here we replaced PHP-FPM with Puma to serve the Ruby application.

    $ ls ~/www/config
    nginx.conf                    # the HTTP server configuration
    puma.rb                       # the application server configuration
    env                           # environment variables used by puma

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

The puma server should be running already, you can restart it this way:

    $ sudo sv restart puma

### Differences with Laravel

Instead of Composer, you’ll use Bundler and Ruby Gems.

### Ruby on Rail 5.0.0 beta1

There is a demonstration video from @dhh on
[youtube](https://www.youtube.com/watch?v=n0WUjGkDFS0).

    $ gem install --prerelease rails
    $ rails --version
    Rails 5.0.0.beta1

I've tested it and it's neat!

{% include 'README-footer.md' %}
