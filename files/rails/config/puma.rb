#!/usr/bin/env puma

#environment "staging"
environment "production"

threads 0, 16
workers 2

directory "/var/www/app"
bind "unix:///tmp/puma.sock"

plugin :tmp_restart

stdout_redirect "/var/www/logs/puma.out.log", "/var/www/logs/puma.err.log", true
