{# vim: set ft=jinja: -#}
#!/usr/bin/env puma

environment "development"

directory "/var/www/app"
bind "unix:///var/www/logs/puma.sock"
