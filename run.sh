#!/bin/sh
echo "Make sure that a proper settings.ini is in the cwd"
PYTHONPATH=lib LC_CTYPE=en_GB.UTF-8 python src/main.py $1
