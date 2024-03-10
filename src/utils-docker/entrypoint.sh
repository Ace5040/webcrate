#!/bin/sh

env | sed 's/^\(.*\)$/export \1/g' > /docker.env
exec crond -f
