#!/bin/bash
/sitesbox/generate_configs.sh
nginx -g 'daemon off;'
