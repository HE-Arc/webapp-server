run lambda { |env| [
  200,
  {"Content-Type": "text/html; charset=utf-8"},
  StringIO.new("<!DOCTYPE html><meta charset=utf-8><title>Hello Ruby!</title><h1>Hello Ruby!</h1></html>")
] }
