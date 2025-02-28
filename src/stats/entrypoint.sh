#!/bin/bash

env | sed 's/^\(.*\)$/export \1/g' > /docker.env
cp /supervisord.conf.template /etc/supervisord.conf
/usr/bin/supervisord -c /etc/supervisord.conf
