#!/bin/bash

/webcrate/parse-configs.py
env | sed 's/^\(.*\)$/export \1/g' > /docker.env
exec systemctl init
