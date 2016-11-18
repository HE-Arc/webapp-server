{# vim: set ft=jinja: -#} {% block header %}

# README

Welcome aboard!

{% endblock -%}

{% block body %}

## Files

The `www` directory is shared with your group, everything else is yours.

`README.md` is this file.

The funny message comes from `~/.bash_profile`.

Feel free to adapt the git configuration in `~/.gitconfig`.

## MySQL

Connect to MySQL (hint: `echo \$PASSWORD`):

```
$ mysql --user $GROUPNAME --host mysql --password
```

{% endblock -%}

{% block footer %}

## Troubleshooting

Do you have a problem or need anything? Send us an issue or come have a chat:

- <https://github.com/HE-Arc/webapp-server/issues>
- <https://gitter.im/HE-Arc/webapp-server> {% endblock -%}
