#!/bin/bash

env | sed 's/^\(.*\)$/export \1/g' > /docker.env
exec systemctl init
