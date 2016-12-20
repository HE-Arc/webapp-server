{# vim: set ft=jinja: -#}
#!/usr/bin/env puma

#environment "staging"
environment "production"

threads 0, 16
workers 2

directory "/var/www/app"
bind "unix:///tmp/puma.sock"

stdout_redirect "/var/www/logs/puma.out", "/var/www/logs/puma.err", true
