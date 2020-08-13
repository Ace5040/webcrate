#!/bin/bash
/webcrate/parse-users.py
nginx -g 'daemon off;'
