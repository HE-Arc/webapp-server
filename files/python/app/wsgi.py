import os


def application(environ, start_response):
    body = (
        "<!DOCTYPE html>"
        "<meta charset=utf-8>"
        "<title>Hello Python!</title>"
        "<style>"
        "body {font:14px sans-serif;color:#444;margin:0 auto;max-width:40em}"
        "img {max-width:100%}"
        "dd+dt {margin-top:1em}"
        "</style>"
        "<h1>Hello Python!</h1>"
        "<p><img src=nginx-uwsgi.png alt='Powered by NGinx + uWSGI'>"
        "<h2>ENV</h2>"
        "<dl>",
        *(f"<dt>{k}<dd>{v}"
          for e in (environ, os.environ)
          for k, v in e.items()
          if k not in ("PASSWORD", "APP_KEY", "SECRET_KEY", "SECRET_KEY_BASE")),
        "</dl>")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])

    for data in body:
        yield data.encode("utf-8")
