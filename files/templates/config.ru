run lambda { |env| [
  200,
  {"Content-Type": "text/html; charset=utf-8"},
  [
    "<!DOCTYPE html><meta charset=utf-8><title>Hello Ruby!</title>",
    "<style>body {font:14px sans-serif;color:#444;margin:0 auto;max-width:40em}img{max-width:100%}dd+dt{margin-top:1em}</style>",
    "<h1>Hello Ruby!</h1>",
    "<img src=uwsgi-nginx.jpg alt='Powered by uWSGI + NGinx'>",
    "<h2>ENV</h2>",
    "<dl>",
    ENV.collect { |k,v| "<dt>#{k}</dt><dd>#{v}</dd>" }.flatten.join(""),
    "</dl>",
    "</html>"
  ]
] }
