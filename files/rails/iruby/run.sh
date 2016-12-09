#!/bin/sh

set -e

. .venv/bin/activate
HOME=`pwd`/.venv
exec $GEM_HOME/bin/iruby notebook --config=.jupyter-config.py
