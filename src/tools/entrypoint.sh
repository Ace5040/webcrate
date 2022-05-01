#!/bin/bash

/webcrate/scripts/init-configs.py
env | sed 's/^\(.*\)$/export \1/g' > /docker.env
exec systemctl init
