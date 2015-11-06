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
    $ rails new blog
    $ cd blog
    $ bundle install --deployment

### Running the server

Nothing to see here! I should work as is.

### Differences with Laravel

Instead of Composer, you’ll use Bundler and Ruby Gems.

### Installing global gems

If you wished to install extra ruby gems.

    $ rvmsudo gem install rails

{% include 'README-footer.md' -%}

### Configuring the database


