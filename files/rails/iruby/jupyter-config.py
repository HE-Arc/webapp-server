{#- vim: set ft=jinja: -#}

c.NotebookApp.ip = '*'
c.NotebookApp.password = '{{ environ.get('PASSWORD', '') | passwd }}'
