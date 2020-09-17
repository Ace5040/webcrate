#!/bin/bash

/webcrate/parse-users.py
/webcrate/parse-services.py
env | sed 's/^\(.*\)$/export \1/g' > /docker.env
exec systemctl init
