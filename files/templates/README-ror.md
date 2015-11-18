{# vim: set ft=jinja: -#}
# README

Here we are again!

## Ruby on Rails

Most of the stuff required are installed by default as you can see.

    $ ruby --version
    ruby 2.2.1p85 (2015-02-26 revision 49769) [x86_64-linux]
    $ rails --version
    Rails 4.2.4

### Creation of a Ruby on Rails web application

    $ cd www
    $ rails new blog --database=postgres|mysql
    $ cd blog
    $ bundle install --deployment

### Configure the database.yml file

    production:
      <<: *default
      database: <->
      adapter: postgresql
      encoding: unicode
      pool: 5
      timeout: 5000
      database: <%= ENV['POSTGRES_USERNAME'] %>
      username: <%= ENV['POSTGRES_USERNAME'] %>
      password: <%= ENV['POSTGRES_PASSWORD'] %>

### Run the migrations.

    $ export RAILS_ENV=production
    $ rake db:create
    $ rake db:migrate


### Running the server

Nothing to see here! I should work as is.

### Differences with Laravel

Instead of Composer, you’ll use Bundler and Ruby Gems.

### Installing global gems

If you wish to install extra ruby gems globally, use rvmsudo:

    $ rvmsudo gem install rails

{% include 'README-footer.md' -%}
